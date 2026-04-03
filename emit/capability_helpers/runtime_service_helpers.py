from __future__ import annotations

def _emit_deep_link_get_launch_uri_method() -> list[str]:
    return [
        ".method public static getLaunchUri(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 4",
        "    if-eqz p0, :ahnali_deep_link_fallback",
        "    :ahnali_deep_link_try_start",
        "    invoke-static {p0}, Lcom/ahnali/runtime/DeepLinkHelper;->getLaunchUriError(Landroid/app/Activity;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_deep_link_fallback",
        "    invoke-virtual {p0}, Landroid/app/Activity;->getIntent()Landroid/content/Intent;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_deep_link_fallback",
        "    invoke-virtual {v1}, Landroid/content/Intent;->getDataString()Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_deep_link_fallback",
        "    return-object v2",
        "    :ahnali_deep_link_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_deep_link_try_start .. :ahnali_deep_link_try_end} :ahnali_deep_link_fallback",
        "    :ahnali_deep_link_fallback",
        "    return-object p1",
        ".end method",
    ]


def _emit_deep_link_get_launch_uri_error_method() -> list[str]:
    return [
        ".method public static getLaunchUriError(Landroid/app/Activity;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_deep_link_invalid",
        "    :ahnali_deep_link_error_try_start",
        "    invoke-virtual {p0}, Landroid/app/Activity;->getIntent()Landroid/content/Intent;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_deep_link_invalid",
        "    invoke-virtual {v1}, Landroid/content/Intent;->getDataString()Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_deep_link_invalid",
        "    invoke-virtual {v2}, Ljava/lang/String;->length()I",
        "    move-result v3",
        "    if-lez v3, :ahnali_deep_link_invalid",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_deep_link_error_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_deep_link_error_try_start .. :ahnali_deep_link_error_try_end} :ahnali_deep_link_exception",
        "    :ahnali_deep_link_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_deep_link_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_work_ensure_store_method() -> list[str]:
    return [
        ".method private static ensureStore()V",
        "    .locals 1",
        "    sget-object v0, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    if-nez v0, :ahnali_work_store_ready",
        "    new-instance v0, Ljava/util/HashMap;",
        "    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    :ahnali_work_store_ready",
        "    return-void",
        ".end method",
    ]


def _emit_work_enqueue_error_method() -> list[str]:
    return [
        ".method public static enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_work_enqueue_invalid",
        "    if-eqz p1, :ahnali_work_enqueue_invalid",
        "    if-ltz p2, :ahnali_work_enqueue_delay_invalid",
        "    :ahnali_work_enqueue_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/WorkHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    const/4 v1, 0x1",
        "    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    invoke-virtual {v0, p1, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_work_enqueue_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_work_enqueue_try_start .. :ahnali_work_enqueue_try_end} :ahnali_work_enqueue_exception",
        "    :ahnali_work_enqueue_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_work_enqueue_delay_invalid",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_work_enqueue_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_work_enqueue_method() -> list[str]:
    return [
        ".method public static enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/WorkHelper;->enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_work_enqueue_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_work_enqueue_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_work_cancel_error_method() -> list[str]:
    return [
        ".method public static cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 3",
        "    if-eqz p0, :ahnali_work_cancel_invalid",
        "    if-eqz p1, :ahnali_work_cancel_invalid",
        "    :ahnali_work_cancel_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/WorkHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v0, p1}, Ljava/util/HashMap;->remove(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_work_cancel_missing",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_work_cancel_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_work_cancel_try_start .. :ahnali_work_cancel_try_end} :ahnali_work_cancel_exception",
        "    :ahnali_work_cancel_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_work_cancel_missing",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_work_cancel_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_work_cancel_method() -> list[str]:
    return [
        ".method public static cancelWork(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/WorkHelper;->cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_work_cancel_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_work_cancel_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_work_status_error_method() -> list[str]:
    return [
        ".method public static getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_work_status_invalid",
        "    if-eqz p1, :ahnali_work_status_invalid",
        "    :ahnali_work_status_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/WorkHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v0, p1}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_work_status_missing",
        "    check-cast v1, Ljava/lang/Integer;",
        "    invoke-virtual {v1}, Ljava/lang/Integer;->intValue()I",
        "    move-result v2",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_work_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_work_status_try_start .. :ahnali_work_status_try_end} :ahnali_work_status_exception",
        "    :ahnali_work_status_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_work_status_missing",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_work_status_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_work_status_method() -> list[str]:
    return [
        ".method public static getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_work_status_fallback",
        "    if-eqz p1, :ahnali_work_status_fallback",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/WorkHelper;->getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_work_status_fallback",
        "    invoke-static {}, Lcom/ahnali/runtime/WorkHelper;->ensureStore()V",
        "    sget-object v1, Lcom/ahnali/runtime/WorkHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v1, p1}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_work_status_fallback",
        "    check-cast v2, Ljava/lang/Integer;",
        "    invoke-virtual {v2}, Ljava/lang/Integer;->intValue()I",
        "    move-result v3",
        "    return v3",
        "    :ahnali_work_status_fallback",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_alarm_ensure_store_method() -> list[str]:
    return [
        ".method private static ensureStore()V",
        "    .locals 1",
        "    sget-object v0, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    if-nez v0, :ahnali_alarm_store_ready",
        "    new-instance v0, Ljava/util/HashMap;",
        "    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    :ahnali_alarm_store_ready",
        "    return-void",
        ".end method",
    ]


def _emit_alarm_schedule_error_method() -> list[str]:
    return [
        ".method public static scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_alarm_schedule_invalid",
        "    if-eqz p1, :ahnali_alarm_schedule_invalid",
        "    if-ltz p2, :ahnali_alarm_schedule_delay_invalid",
        "    :ahnali_alarm_schedule_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/AlarmHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    const/4 v1, 0x1",
        "    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    invoke-virtual {v0, p1, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_alarm_schedule_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_alarm_schedule_try_start .. :ahnali_alarm_schedule_try_end} :ahnali_alarm_schedule_exception",
        "    :ahnali_alarm_schedule_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_alarm_schedule_delay_invalid",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_alarm_schedule_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_alarm_schedule_method() -> list[str]:
    return [
        ".method public static scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/AlarmHelper;->scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_alarm_schedule_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_alarm_schedule_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_alarm_cancel_error_method() -> list[str]:
    return [
        ".method public static cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 3",
        "    if-eqz p0, :ahnali_alarm_cancel_invalid",
        "    if-eqz p1, :ahnali_alarm_cancel_invalid",
        "    :ahnali_alarm_cancel_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/AlarmHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v0, p1}, Ljava/util/HashMap;->remove(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_alarm_cancel_missing",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_alarm_cancel_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_alarm_cancel_try_start .. :ahnali_alarm_cancel_try_end} :ahnali_alarm_cancel_exception",
        "    :ahnali_alarm_cancel_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_alarm_cancel_missing",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_alarm_cancel_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_alarm_cancel_method() -> list[str]:
    return [
        ".method public static cancelAlarm(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/AlarmHelper;->cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_alarm_cancel_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_alarm_cancel_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_alarm_status_error_method() -> list[str]:
    return [
        ".method public static getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_alarm_status_invalid",
        "    if-eqz p1, :ahnali_alarm_status_invalid",
        "    :ahnali_alarm_status_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/AlarmHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v0, p1}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_alarm_status_missing",
        "    check-cast v1, Ljava/lang/Integer;",
        "    invoke-virtual {v1}, Ljava/lang/Integer;->intValue()I",
        "    move-result v2",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_alarm_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_alarm_status_try_start .. :ahnali_alarm_status_try_end} :ahnali_alarm_status_exception",
        "    :ahnali_alarm_status_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_alarm_status_missing",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_alarm_status_exception",
        "    const/4 v0, 0x3",
        "    return v0",
        ".end method",
    ]


def _emit_alarm_status_method() -> list[str]:
    return [
        ".method public static getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_alarm_status_fallback",
        "    if-eqz p1, :ahnali_alarm_status_fallback",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/AlarmHelper;->getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_alarm_status_fallback",
        "    invoke-static {}, Lcom/ahnali/runtime/AlarmHelper;->ensureStore()V",
        "    sget-object v1, Lcom/ahnali/runtime/AlarmHelper;->sStatusByName:Ljava/util/HashMap;",
        "    invoke-virtual {v1, p1}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_alarm_status_fallback",
        "    check-cast v2, Ljava/lang/Integer;",
        "    invoke-virtual {v2}, Ljava/lang/Integer;->intValue()I",
        "    move-result v3",
        "    return v3",
        "    :ahnali_alarm_status_fallback",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_job_ensure_store_method() -> list[str]:
    return [
        ".method private static ensureStore()V",
        "    .locals 1",
        "    sget-object v0, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    if-nez v0, :ahnali_job_store_ready",
        "    new-instance v0, Ljava/util/HashMap;",
        "    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    :ahnali_job_store_ready",
        "    return-void",
        ".end method",
    ]


def _emit_job_schedule_error_method() -> list[str]:
    return [
        ".method public static scheduleJobError(Landroid/app/Activity;II)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_job_schedule_invalid",
        "    if-lez p1, :ahnali_job_schedule_invalid",
        "    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v1, 0x15",
        "    if-lt v0, v1, :ahnali_job_schedule_unsupported",
        "    if-ltz p2, :ahnali_job_schedule_delay_invalid",
        "    :ahnali_job_schedule_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/JobHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    const/4 v3, 0x1",
        "    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v4",
        "    invoke-virtual {v0, v2, v4}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_job_schedule_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_job_schedule_try_start .. :ahnali_job_schedule_try_end} :ahnali_job_schedule_exception",
        "    :ahnali_job_schedule_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_job_schedule_unsupported",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_job_schedule_delay_invalid",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_job_schedule_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_job_schedule_method() -> list[str]:
    return [
        ".method public static scheduleJob(Landroid/app/Activity;II)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/JobHelper;->scheduleJobError(Landroid/app/Activity;II)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_job_schedule_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_job_schedule_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_job_cancel_error_method() -> list[str]:
    return [
        ".method public static cancelJobError(Landroid/app/Activity;I)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_job_cancel_invalid",
        "    if-lez p1, :ahnali_job_cancel_invalid",
        "    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v1, 0x15",
        "    if-lt v0, v1, :ahnali_job_cancel_unsupported",
        "    :ahnali_job_cancel_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/JobHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    invoke-virtual {v0, v2}, Ljava/util/HashMap;->remove(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_job_cancel_missing",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_job_cancel_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_job_cancel_try_start .. :ahnali_job_cancel_try_end} :ahnali_job_cancel_exception",
        "    :ahnali_job_cancel_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_job_cancel_unsupported",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_job_cancel_missing",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_job_cancel_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_job_cancel_method() -> list[str]:
    return [
        ".method public static cancelJob(Landroid/app/Activity;I)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/JobHelper;->cancelJobError(Landroid/app/Activity;I)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_job_cancel_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_job_cancel_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_job_status_error_method() -> list[str]:
    return [
        ".method public static getJobStatusError(Landroid/app/Activity;I)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_job_status_invalid",
        "    if-lez p1, :ahnali_job_status_invalid",
        "    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v1, 0x15",
        "    if-lt v0, v1, :ahnali_job_status_unsupported",
        "    :ahnali_job_status_try_start",
        "    invoke-static {}, Lcom/ahnali/runtime/JobHelper;->ensureStore()V",
        "    sget-object v0, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    invoke-virtual {v0, v2}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_job_status_missing",
        "    check-cast v3, Ljava/lang/Integer;",
        "    invoke-virtual {v3}, Ljava/lang/Integer;->intValue()I",
        "    move-result v4",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_job_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_job_status_try_start .. :ahnali_job_status_try_end} :ahnali_job_status_exception",
        "    :ahnali_job_status_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_job_status_unsupported",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_job_status_missing",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_job_status_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_job_status_method() -> list[str]:
    return [
        ".method public static getJobStatus(Landroid/app/Activity;I)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_job_status_fallback",
        "    if-lez p1, :ahnali_job_status_fallback",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/JobHelper;->getJobStatusError(Landroid/app/Activity;I)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_job_status_fallback",
        "    invoke-static {}, Lcom/ahnali/runtime/JobHelper;->ensureStore()V",
        "    sget-object v1, Lcom/ahnali/runtime/JobHelper;->sStatusByJobId:Ljava/util/HashMap;",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v2",
        "    invoke-virtual {v1, v2}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_job_status_fallback",
        "    check-cast v3, Ljava/lang/Integer;",
        "    invoke-virtual {v3}, Ljava/lang/Integer;->intValue()I",
        "    move-result v4",
        "    return v4",
        "    :ahnali_job_status_fallback",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def append_runtime_service_helpers(*, lines: list[str], class_desc: str, helper_method: str, helper_sig: str) -> bool:
    if (
        class_desc == "Lcom/ahnali/runtime/DeepLinkHelper;"
        and helper_method == "getLaunchUri"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ):
        lines.extend(_emit_deep_link_get_launch_uri_method())
        lines.append("")
        lines.extend(_emit_deep_link_get_launch_uri_error_method())
        return True

    if (
        class_desc == "Lcom/ahnali/runtime/WorkHelper;"
        and helper_method == "enqueueWork"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;I)I"
    ):
        lines.insert(3, ".field private static sStatusByName:Ljava/util/HashMap;")
        lines.insert(4, "")
        lines.extend(_emit_work_ensure_store_method())
        lines.append("")
        lines.extend(_emit_work_enqueue_method())
        lines.append("")
        lines.extend(_emit_work_enqueue_error_method())
        lines.append("")
        lines.extend(_emit_work_cancel_method())
        lines.append("")
        lines.extend(_emit_work_cancel_error_method())
        lines.append("")
        lines.extend(_emit_work_status_method())
        lines.append("")
        lines.extend(_emit_work_status_error_method())
        return True

    if (
        class_desc == "Lcom/ahnali/runtime/AlarmHelper;"
        and helper_method == "scheduleAlarm"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;I)I"
    ):
        lines.insert(3, ".field private static sStatusByName:Ljava/util/HashMap;")
        lines.insert(4, "")
        lines.extend(_emit_alarm_ensure_store_method())
        lines.append("")
        lines.extend(_emit_alarm_schedule_method())
        lines.append("")
        lines.extend(_emit_alarm_schedule_error_method())
        lines.append("")
        lines.extend(_emit_alarm_cancel_method())
        lines.append("")
        lines.extend(_emit_alarm_cancel_error_method())
        lines.append("")
        lines.extend(_emit_alarm_status_method())
        lines.append("")
        lines.extend(_emit_alarm_status_error_method())
        return True

    if (
        class_desc == "Lcom/ahnali/runtime/JobHelper;"
        and helper_method == "scheduleJob"
        and helper_sig == "(Landroid/app/Activity;II)I"
    ):
        lines.insert(3, ".field private static sStatusByJobId:Ljava/util/HashMap;")
        lines.insert(4, "")
        lines.extend(_emit_job_ensure_store_method())
        lines.append("")
        lines.extend(_emit_job_schedule_method())
        lines.append("")
        lines.extend(_emit_job_schedule_error_method())
        lines.append("")
        lines.extend(_emit_job_cancel_method())
        lines.append("")
        lines.extend(_emit_job_cancel_error_method())
        lines.append("")
        lines.extend(_emit_job_status_method())
        lines.append("")
        lines.extend(_emit_job_status_error_method())
        return True

    return False
