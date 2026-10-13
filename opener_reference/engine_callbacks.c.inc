/* Communication-only diagnostics. This code never fabricates an inspection.
 * PLC output150: Request, EStop_OK, Mc_Run, Stop_PB (four little-endian slots).
 * PLC input100: Result, Done (two slots). Done remains false without a bridge.
 */
static unsigned long engine_updates = 0;
static unsigned long engine_sends = 0;
static unsigned long engine_opens = 0;
static unsigned long engine_timeouts = 0;
static int engine_connected = 0;
static int engine_run = 0;
static int engine_seen = 0;
static double engine_last_receive = 0.0;
static double engine_last_status = -1.0;

static double EngineMonotonic(void) {
  struct timespec value;
  if (clock_gettime(CLOCK_MONOTONIC, &value) != 0) return 0.0;
  return (double)value.tv_sec + (double)value.tv_nsec / 1000000000.0;
}

static unsigned int EngineSlot(unsigned int slot) {
  return (unsigned int)g_assembly_data096[2 * slot]
       | ((unsigned int)g_assembly_data096[2 * slot + 1] << 8);
}

static void WriteEngineStatus(int force) {
  const char *path = getenv("ENGINE_OPENER_STATUS");
  char temporary[4096];
  unsigned int values[4];
  int bool_valid = 1;
  double now = EngineMonotonic();
  if (path == NULL || path[0] != '/' || strlen(path) > 4000) return;
  if (!force && now - engine_last_status < 0.1) return;
  engine_last_status = now;
  for (unsigned int i = 0; i < 4; ++i) {
    values[i] = EngineSlot(i);
    if (values[i] > 1) bool_valid = 0;
  }
  snprintf(temporary, sizeof(temporary), "%s.tmp.%ld", path, (long)getpid());
  FILE *file = fopen(temporary, "w");
  if (file == NULL) return;
  fprintf(file,
    "{\"schema\":1,\"pid\":%ld,\"mode\":\"COMMUNICATION_ONLY_RESULT_DISARMED\","
    "\"monotonic_s\":%.6f,\"connected\":%s,\"run_idle_run\":%s,"
    "\"assembly_updates\":%lu,\"production_callbacks\":%lu,\"opens\":%lu,\"timeouts\":%lu,"
    "\"has_received\":%s,\"last_receive_monotonic_s\":%.6f,\"bool_slots_valid\":%s,"
    "\"controls_valid\":%s,\"raw150_hex\":\"",
    (long)getpid(), now, engine_connected ? "true" : "false",
    (engine_connected && engine_seen && engine_run) ? "true" : "false",
    engine_updates, engine_sends, engine_opens, engine_timeouts,
    engine_seen ? "true" : "false", engine_last_receive, bool_valid ? "true" : "false",
    (engine_connected && engine_run && engine_seen && bool_valid) ? "true" : "false");
  for (unsigned int i = 0; i < sizeof(g_assembly_data096); ++i)
    fprintf(file, "%02x", (unsigned int)g_assembly_data096[i]);
  fprintf(file,
    "\",\"slots\":{\"Inspection_Request\":%u,\"EStop_OK\":%u,\"Mc_Run\":%u,\"Stop_PB\":%u},"
    "\"raw100_hex\":\"00000000\",\"publication_enabled\":false,\"inspection_bridge\":\"NOT_IMPLEMENTED\"}\n",
    values[0], values[1], values[2], values[3]);
  if (fclose(file) == 0) {
    if (rename(temporary, path) != 0) unlink(temporary);
  } else unlink(temporary);
}

void HandleApplication(void) {
  WriteEngineStatus(0);
}

void CheckIoConnectionEvent(unsigned int output_assembly_id,
                            unsigned int input_assembly_id,
                            IoConnectionEvent event) {
  if (output_assembly_id != 150 || input_assembly_id != 100) return;
  engine_connected = (event == kIoConnectionEventOpened);
  engine_seen = 0;
  /* OpENer caches the last header across connections and invokes RunIdleChanged
   * only when it changes. Keep that mirror; has_received gates every new link. */
  if (event == kIoConnectionEventOpened) ++engine_opens;
  if (event == kIoConnectionEventTimedOut) ++engine_timeouts;
  memset(g_assembly_data064, 0, sizeof(g_assembly_data064));
  WriteEngineStatus(1);
}

EipStatus AfterAssemblyDataReceived(CipInstance *instance) {
  if (instance->instance_number == 150) {
    ++engine_updates;
    engine_seen = 1;
    engine_last_receive = EngineMonotonic();
  }
  /* No input echo. Result=0 alone is not PASS; Done stays false. */
  memset(g_assembly_data064, 0, sizeof(g_assembly_data064));
  WriteEngineStatus(0);
  return kEipStatusOk;
}

EipBool8 BeforeAssemblyDataSend(CipInstance *instance) {
  if (instance->instance_number == 100) ++engine_sends;
  memset(g_assembly_data064, 0, sizeof(g_assembly_data064));
  WriteEngineStatus(0);
  return true;
}
