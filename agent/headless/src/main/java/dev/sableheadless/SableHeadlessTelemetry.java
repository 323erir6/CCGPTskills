package dev.sableheadless;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.logging.LogUtils;
import dev.ryanhcode.sable.api.physics.mass.MassData;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.companion.math.BoundingBox3dc;
import dev.ryanhcode.sable.companion.math.Pose3dc;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.SubLevel;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import org.joml.Quaterniondc;
import org.joml.Vector3dc;

@Mod(SableHeadlessTelemetry.MOD_ID)
public final class SableHeadlessTelemetry {
    public static final String MOD_ID = "sable_headless_telemetry";
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
    private static Session activeSession;

    public SableHeadlessTelemetry() {
        NeoForge.EVENT_BUS.addListener(SableHeadlessTelemetry::onServerStarted);
        NeoForge.EVENT_BUS.addListener(SableHeadlessTelemetry::onServerTick);
        NeoForge.EVENT_BUS.addListener(SableHeadlessTelemetry::onServerStopping);
    }

    private static void onServerStarted(ServerStartedEvent event) {
        String scenarioPath = System.getenv("SABLE_SIM_SCENARIO");
        if (scenarioPath == null || scenarioPath.isBlank()) {
            LOGGER.info("Sable headless telemetry is idle; SABLE_SIM_SCENARIO is not set");
            return;
        }
        try {
            Scenario scenario = Scenario.load(Path.of(scenarioPath));
            String outputValue = System.getenv("SABLE_SIM_OUTPUT");
            Path output = outputValue == null || outputValue.isBlank()
                    ? Path.of("agent-results", "headless-report.json")
                    : Path.of(outputValue);
            activeSession = new Session(event.getServer(), scenario, output.toAbsolutePath().normalize());
            LOGGER.info("Started real Sable headless scenario '{}' for {} ticks", scenario.name, scenario.durationTicks);
        } catch (Exception error) {
            LOGGER.error("Cannot start Sable headless scenario", error);
            event.getServer().halt(false);
        }
    }

    private static void onServerTick(ServerTickEvent.Post event) {
        Session session = activeSession;
        if (session == null) return;
        try {
            session.tick();
        } catch (Throwable error) {
            LOGGER.error("Sable headless scenario failed", error);
            session.fail(error);
        }
    }

    private static void onServerStopping(ServerStoppingEvent event) {
        Session session = activeSession;
        activeSession = null;
        if (session != null && !session.finished) {
            session.fail(new IllegalStateException("server stopped before the scenario completed"));
        }
    }

    private record ScheduledCommand(int tick, String command, boolean requireSuccess) {
        private static ScheduledCommand parse(JsonObject value) {
            int tick = value.get("tick").getAsInt();
            String command = value.get("command").getAsString().trim();
            boolean requireSuccess = !value.has("require_success") || value.get("require_success").getAsBoolean();
            if (tick < 0 || command.isEmpty() || command.length() > 2048 || command.startsWith("/")) {
                throw new IllegalArgumentException("invalid scheduled command");
            }
            return new ScheduledCommand(tick, command, requireSuccess);
        }
    }

    private static final class Scenario {
        private final String name;
        private final int durationTicks;
        private final int sampleEvery;
        private final int expectMinSublevels;
        private final boolean stopServer;
        private final List<ScheduledCommand> commands;

        private Scenario(String name, int durationTicks, int sampleEvery, int expectMinSublevels,
                         boolean stopServer, List<ScheduledCommand> commands) {
            this.name = name;
            this.durationTicks = durationTicks;
            this.sampleEvery = sampleEvery;
            this.expectMinSublevels = expectMinSublevels;
            this.stopServer = stopServer;
            this.commands = commands;
        }

        private static Scenario load(Path path) throws IOException {
            JsonObject root = GSON.fromJson(Files.readString(path, StandardCharsets.UTF_8), JsonObject.class);
            if (root == null || !root.has("schema_version") || root.get("schema_version").getAsInt() != 1) {
                throw new IllegalArgumentException("schema_version must be 1");
            }
            String name = root.has("name") ? root.get("name").getAsString().trim() : "headless-sable";
            int duration = root.has("duration_ticks") ? root.get("duration_ticks").getAsInt() : 200;
            int sampleEvery = root.has("sample_every") ? root.get("sample_every").getAsInt() : 1;
            int expectMin = root.has("expect_min_sublevels") ? root.get("expect_min_sublevels").getAsInt() : 1;
            boolean stopServer = !root.has("stop_server") || root.get("stop_server").getAsBoolean();
            if (name.isEmpty() || name.length() > 128 || duration < 1 || duration > 12000
                    || sampleEvery < 1 || sampleEvery > duration || expectMin < 0 || expectMin > 1024) {
                throw new IllegalArgumentException("invalid bounded scenario settings");
            }
            List<ScheduledCommand> commands = new ArrayList<>();
            JsonArray array = root.has("commands") ? root.getAsJsonArray("commands") : new JsonArray();
            if (array.size() > 100) throw new IllegalArgumentException("at most 100 commands are allowed");
            for (JsonElement element : array) commands.add(ScheduledCommand.parse(element.getAsJsonObject()));
            commands.sort(Comparator.comparingInt(ScheduledCommand::tick));
            if (!commands.isEmpty() && commands.getLast().tick >= duration) {
                throw new IllegalArgumentException("command tick must be below duration_ticks");
            }
            return new Scenario(name, duration, sampleEvery, expectMin, stopServer, List.copyOf(commands));
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final Scenario scenario;
        private final Path output;
        private final JsonObject report = new JsonObject();
        private final JsonArray samples = new JsonArray();
        private final JsonArray commandResults = new JsonArray();
        private int tick;
        private boolean finished;
        private int maximumSublevels;

        private Session(MinecraftServer server, Scenario scenario, Path output) {
            this.server = server;
            this.scenario = scenario;
            this.output = output;
            report.addProperty("schema_version", 1);
            report.addProperty("engine", "real NeoForge dedicated server with original Sable and mod JARs");
            report.addProperty("scenario", scenario.name);
            report.addProperty("started_at", Instant.now().toString());
            report.addProperty("minecraft", "1.21.1");
            report.addProperty("neoforge", "21.1.248");
            report.add("loaded_mods", loadedMods());
            report.add("commands", commandResults);
            report.add("samples", samples);
        }

        private void tick() {
            for (ScheduledCommand command : scenario.commands) {
                if (command.tick != tick) continue;
                int result;
                try {
                    result = server.getCommands().getDispatcher().execute(
                            command.command, server.createCommandSourceStack().withPermission(4));
                } catch (Exception error) {
                    throw new IllegalStateException("command exception at tick " + tick + ": " + command.command, error);
                }
                JsonObject record = new JsonObject();
                record.addProperty("tick", tick);
                record.addProperty("command", command.command);
                record.addProperty("result", result);
                commandResults.add(record);
                if (command.requireSuccess && result <= 0) {
                    throw new IllegalStateException("command failed at tick " + tick + ": " + command.command);
                }
            }
            if (tick % scenario.sampleEvery == 0 || tick == scenario.durationTicks - 1) {
                JsonObject sample = capture(server, tick);
                samples.add(sample);
                maximumSublevels = Math.max(maximumSublevels, sample.get("sublevel_count").getAsInt());
            }
            tick++;
            if (tick >= scenario.durationTicks) complete();
        }

        private void complete() {
            if (finished) return;
            finished = true;
            boolean passed = maximumSublevels >= scenario.expectMinSublevels;
            report.addProperty("status", passed ? "passed" : "failed");
            report.addProperty("ticks_executed", tick);
            report.addProperty("maximum_sublevels", maximumSublevels);
            report.addProperty("expected_min_sublevels", scenario.expectMinSublevels);
            report.addProperty("fidelity", "live-server-executed; exact only for the recorded mod/config/world inputs");
            write();
            activeSession = null;
            if (scenario.stopServer) server.halt(false);
        }

        private void fail(Throwable error) {
            if (finished) return;
            finished = true;
            report.addProperty("status", "error");
            report.addProperty("ticks_executed", tick);
            report.addProperty("error", error.getClass().getName() + ": " + String.valueOf(error.getMessage()));
            try {
                write();
            } finally {
                activeSession = null;
                server.halt(false);
            }
        }

        private void write() {
            try {
                Path parent = output.getParent();
                if (parent != null) Files.createDirectories(parent);
                Files.writeString(output, GSON.toJson(report) + System.lineSeparator(), StandardCharsets.UTF_8);
                LOGGER.info("Wrote Sable headless report to {}", output);
            } catch (IOException error) {
                throw new IllegalStateException("cannot write Sable report to " + output, error);
            }
        }
    }

    private static JsonArray loadedMods() {
        JsonArray result = new JsonArray();
        ModList.get().getMods().stream()
                .sorted(Comparator.comparing(info -> info.getModId().toLowerCase(Locale.ROOT)))
                .forEach(info -> {
                    JsonObject value = new JsonObject();
                    value.addProperty("id", info.getModId());
                    value.addProperty("version", info.getVersion().toString());
                    result.add(value);
                });
        return result;
    }

    private static JsonObject capture(MinecraftServer server, int scenarioTick) {
        JsonObject sample = new JsonObject();
        sample.addProperty("scenario_tick", scenarioTick);
        sample.addProperty("server_tick", server.getTickCount());
        JsonArray dimensions = new JsonArray();
        int total = 0;
        for (ServerLevel level : server.getAllLevels()) {
            JsonObject dimension = new JsonObject();
            dimension.addProperty("id", level.dimension().location().toString());
            JsonArray bodies = captureLevel(level);
            total += bodies.size();
            dimension.add("sublevels", bodies);
            dimensions.add(dimension);
        }
        sample.addProperty("sublevel_count", total);
        sample.add("dimensions", dimensions);
        return sample;
    }

    private static JsonArray captureLevel(ServerLevel level) {
        ServerSubLevelContainer container = SubLevelContainer.getContainer(level);
        JsonArray bodies = new JsonArray();
        if (container == null) return bodies;
        for (SubLevel raw : container.getAllSubLevels()) {
            if (raw instanceof ServerSubLevel body) bodies.add(captureBody(body));
        }
        return bodies;
    }

    private static JsonObject captureBody(ServerSubLevel body) {
        JsonObject result = new JsonObject();
        result.addProperty("uuid", body.getUniqueId().toString());
        String name = body.getName();
        if (name == null) result.add("name", null); else result.addProperty("name", String.valueOf(name));
        result.addProperty("removed", body.isRemoved());
        Pose3dc pose = body.logicalPose();
        result.add("position", vector(pose.position()));
        result.add("orientation", quaternion(pose.orientation()));
        result.add("scale", vector(pose.scale()));
        result.add("linear_velocity", vector(body.latestLinearVelocity));
        result.add("angular_velocity", vector(body.latestAngularVelocity));
        MassData mass = body.getMassTracker();
        result.addProperty("mass", finite(mass.getMass()));
        Vector3dc center = mass.getCenterOfMass();
        if (center != null) result.add("center_of_mass", vector(center));
        result.add("world_bounds", bounds(body.boundingBox()));
        return result;
    }

    private static JsonArray vector(Vector3dc value) {
        JsonArray result = new JsonArray();
        result.add(finite(value.x()));
        result.add(finite(value.y()));
        result.add(finite(value.z()));
        return result;
    }

    private static JsonArray quaternion(Quaterniondc value) {
        JsonArray result = new JsonArray();
        result.add(finite(value.x()));
        result.add(finite(value.y()));
        result.add(finite(value.z()));
        result.add(finite(value.w()));
        return result;
    }

    private static JsonArray bounds(BoundingBox3dc value) {
        JsonArray result = new JsonArray();
        result.add(finite(value.minX()));
        result.add(finite(value.minY()));
        result.add(finite(value.minZ()));
        result.add(finite(value.maxX()));
        result.add(finite(value.maxY()));
        result.add(finite(value.maxZ()));
        return result;
    }

    private static double finite(double value) {
        if (!Double.isFinite(value)) {
            throw new IllegalStateException("Sable returned a non-finite numeric value");
        }
        return value;
    }
}
