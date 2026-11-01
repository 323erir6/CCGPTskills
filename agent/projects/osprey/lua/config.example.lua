-- Copy to config.lua and edit. Peripheral names depend on your assembled craft.
return {
  rocket="OSPREY-01",
  secret="change_this_for_your_server", -- Pairing token, not encryption.
  -- Replace these with actual wired-modem peripheral names from peripheral.getNames().
  engines={"back","left","right","top"},
  fins={pitch_up="fin_0",pitch_down="fin_1",yaw_left="fin_2",yaw_right="fin_3"},
  fin_signs={pitch_up=1,pitch_down=-1,yaw_left=1,yaw_right=-1},
  fin_limit=15,    -- DISPLAY/calibration degrees; verify actual motor unit in-game.
  pitch_sign=1, yaw_sign=1,
  correction_gain=0.8, -- Gameplay prototype; must be calibrated on a tethered test stand.
  target_timeout=3.0, -- seconds without moving-target updates
  control_hz=10,
  burn_seconds=800, -- expected fuel duration; does not create or refill fuel
  auto_assemble_fins=false,
  operator_id=nil, -- Lock to paired pocket computer ID if known.
  allow_control=false, -- Set true ONLY after testing orientation and fin axes.
}
