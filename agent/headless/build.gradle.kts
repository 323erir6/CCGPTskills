plugins {
    java
    id("net.neoforged.moddev") version "2.0.80"
}

version = property("mod_version")!!
group = "dev.sableheadless"

base {
    archivesName.set("sable-headless-telemetry")
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(21))
}

val modpackDirectory = providers.environmentVariable("SABLE_MODPACK_DIR").orNull
    ?: error("Set SABLE_MODPACK_DIR to the Minecraft instance mods directory")
val modpackMode = providers.environmentVariable("SABLE_MODS_MODE").orElse("full").get()
val headlessRunDirectory = providers.environmentVariable("SABLE_HEADLESS_RUN_DIR").orElse("run").get()
val sableJar = file("$modpackDirectory/sable-neoforge-1.21.1-2.0.5.jar")
require(sableJar.isFile) { "Missing exact Sable JAR: $sableJar" }
val extractedCompanionDirectory = layout.buildDirectory.dir("extracted-sable-compile")
val extractSableCompanion by tasks.registering(Copy::class) {
    from(zipTree(sableJar)) {
        include("META-INF/jarjar/sable-companion-common-1.21.1-1.6.0.jar")
        eachFile { path = name }
    }
    includeEmptyDirs = false
    into(extractedCompanionDirectory)
}
val sableCompanionJar = extractedCompanionDirectory.map {
    it.file("sable-companion-common-1.21.1-1.6.0.jar")
}

val runtimeMods = fileTree(modpackDirectory) {
    if (modpackMode == "minimal") {
        include("sable-neoforge-1.21.1-2.0.5.jar")
    } else {
        include("*.jar")
        file("server-excluded-mods.txt").readLines()
            .map(String::trim)
            .filter { it.isNotEmpty() && !it.startsWith("#") }
            .forEach { exclude(it) }
    }
}

neoForge {
    version = property("neo_version") as String
    mods {
        create("sable_headless_telemetry") {
            sourceSet(sourceSets.main.get())
        }
    }
    runs {
        create("server") {
            server()
            gameDirectory = file(headlessRunDirectory)
            programArgument("--nogui")
        }
    }
}

dependencies {
    compileOnly(files(sableJar, sableCompanionJar))
    runtimeOnly(files(runtimeMods))
}

tasks.compileJava {
    dependsOn(extractSableCompanion)
}

tasks.processResources {
    inputs.property("version", project.version)
    filesMatching("META-INF/neoforge.mods.toml") {
        expand("version" to project.version)
    }
}
