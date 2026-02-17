# emit/smali_activity.py

def emit_activity_smali(
    dalvik_blocks,
    reg_map,
    locals_count,
    package="com/ahnali/preview",
    activity="MainActivity",
):
    cls = f"L{package}/{activity};"

    lines = []

    # ---- Class ----
    lines.append(f".class public {cls}")
    lines.append(".super Landroid/app/Activity;")
    lines.append("")

    # ---- Constructor ----
    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 1")
    lines.append("    invoke-direct {p0}, Landroid/app/Activity;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    # ---- onCreate ----
    lines.append(".method protected onCreate(Landroid/os/Bundle;)V")
    lines.append(f"    .locals {locals_count}")
    lines.append("")

    # super.onCreate(p0, p1)
    lines.append(
        "    invoke-super {p0, p1}, "
        "Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V"
    )
    lines.append("")

    # ---- Body (lowered code) ----
    referenced = set()
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            name = instr.__class__.__name__
            if name == "DGoto":
                referenced.add(instr.target.id)
            elif name == "DIf":
                referenced.add(instr.true.id)
                referenced.add(instr.false.id)
            elif name == "DIfZ":
                referenced.add(instr.true.id)
                referenced.add(instr.false.id)
            elif name == "DPackedSwitch":
                referenced.add(instr.default.id)
                referenced.update(target.id for target in instr.targets)
            elif name == "DSparseSwitch":
                referenced.add(instr.default.id)
                referenced.update(target.id for target in instr.targets)

    switch_payloads = []
    switch_payload_idx = 0

    for block in dalvik_blocks.values():
        if block.id not in referenced and not block.instructions:
            continue

        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            name = instr.__class__.__name__

            if name == "DConst":
                r = reg_map[instr.dst]
                if isinstance(instr.value, str):
                    s = instr.value.replace("\\", "\\\\").replace("\"", "\\\"")
                    lines.append(f"    const-string {r}, \"{s}\"")
                elif isinstance(instr.value, float):
                    import struct
                    bits = struct.unpack(">I", struct.pack(">f", instr.value))[0]
                    if bits & 0xFFFF == 0:
                        lines.append(f"    const/high16 {r}, 0x{bits & 0xFFFF0000:08x}")
                    else:
                        lines.append(f"    const {r}, 0x{bits:08x}")
                else:
                    lines.append(f"    const/4 {r}, {instr.value}")
            elif name == "DConstWide":
                r = reg_map[instr.dst]
                if isinstance(instr.value, float):
                    import struct
                    bits = struct.unpack(">Q", struct.pack(">d", instr.value))[0]
                    lines.append(f"    const-wide {r}, 0x{bits:016x}")
                else:
                    lines.append(f"    const-wide {r}, {int(instr.value)}")
            elif name == "DConstStringJumbo":
                r = reg_map[instr.dst]
                s = str(instr.value).replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"    const-string/jumbo {r}, \"{s}\"")
            elif name == "DNew":
                r = reg_map[instr.dst]
                lines.append(f"    new-instance {r}, {instr.class_desc}")

            elif name == "DMove":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move {rd}, {rs}")
            elif name == "DSpillLoad":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                value_type = getattr(getattr(instr.dst, "ssa", None), "type", None)
                if value_type in ("J", "D"):
                    lines.append(f"    move-wide {rd}, {rs}")
                else:
                    lines.append(f"    move {rd}, {rs}")
            elif name == "DSpillStore":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                value_type = getattr(getattr(instr.src, "ssa", None), "type", None)
                if value_type in ("J", "D"):
                    lines.append(f"    move-wide {rd}, {rs}")
                else:
                    lines.append(f"    move {rd}, {rs}")
            elif name == "DMoveWide":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move-wide {rd}, {rs}")
            elif name == "DMoveResult":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result {rd}")
            elif name == "DMoveResultObject":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-object {rd}")
            elif name == "DMoveResultWide":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-wide {rd}")
            elif name == "DMoveException":
                rd = reg_map[instr.dst]
                lines.append(f"    move-exception {rd}")
            elif name == "DMonitorEnter":
                rv = reg_map[instr.value]
                lines.append(f"    monitor-enter {rv}")
            elif name == "DMonitorExit":
                rv = reg_map[instr.value]
                lines.append(f"    monitor-exit {rv}")
            elif name == "DArrayLength":
                rd = reg_map[instr.dst]
                ra = reg_map[instr.array]
                lines.append(f"    array-length {rd}, {ra}")
            elif name == "DFilledNewArray":
                regs = ", ".join(reg_map[a.ssa] for a in instr.args)
                lines.append(
                    f"    filled-new-array {{{regs}}}, {instr.array_desc}"
                )
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-object {rd}")

            elif name in (
                "DAdd",
                "DSub",
                "DMul",
                "DDiv",
                "DRem",
                "DAnd",
                "DOr",
                "DXor",
                "DShl",
                "DShr",
                "DUshr",
            ):
                rd = reg_map[instr.dst]
                ra = reg_map[instr.lhs]
                rb = reg_map[instr.rhs]

                type_desc = getattr(instr, "type_desc", "I")
                if type_desc in ("B", "C", "S", "Z"):
                    type_desc = "I"

                op_base = {
                    "DAdd": "add",
                    "DSub": "sub",
                    "DMul": "mul",
                    "DDiv": "div",
                    "DRem": "rem",
                    "DAnd": "and",
                    "DOr": "or",
                    "DXor": "xor",
                    "DShl": "shl",
                    "DShr": "shr",
                    "DUshr": "ushr",
                }[name]

                if op_base in ("and", "or", "xor", "shl", "shr", "ushr"):
                    suffix = {
                        "I": "int",
                        "J": "long",
                    }.get(type_desc)
                else:
                    suffix = {
                        "I": "int",
                        "J": "long",
                        "F": "float",
                        "D": "double",
                    }.get(type_desc)
                if suffix is None:
                    raise RuntimeError(f"Unsupported binary op type {type_desc}")

                opcode = f"{op_base}-{suffix}"

                lines.append(
                    f"    {opcode} {rd}, {ra}, {rb}"
                )

            elif name == "DCompare":
                rd = reg_map[instr.dst]
                ra = reg_map[instr.lhs]
                rb = reg_map[instr.rhs]
                if instr.cmp_kind == "long":
                    opcode = "cmp-long"
                elif instr.cmp_kind == "float":
                    opcode = "cmpl-float" if instr.nan_mode == "cmpl" else "cmpg-float"
                elif instr.cmp_kind == "double":
                    opcode = "cmpl-double" if instr.nan_mode == "cmpl" else "cmpg-double"
                else:
                    raise RuntimeError(f"Unsupported compare kind {instr.cmp_kind}")
                lines.append(f"    {opcode} {rd}, {ra}, {rb}")

            elif name == "DGoto":
                lines.append(f"    goto :B{instr.target.id}")

            elif name == "DIf":
                if instr.cmp:
                    op, a, b = instr.cmp
                    ra = reg_map[a]
                    rb = reg_map[b]

                    opcode = {
                        "<":  "if-lt",
                        "<=": "if-le",
                        ">":  "if-gt",
                        ">=": "if-ge",
                        "==": "if-eq",
                        "!=": "if-ne",
                    }[op]

                    lines.append(
                        f"    {opcode} {ra}, {rb}, :B{instr.true.id}"
                    )
                    lines.append(
                        f"    goto :B{instr.false.id}"
                    )
            elif name == "DIfZ":
                r = reg_map[instr.cond]
                lines.append(
                    f"    if-{instr.op} {r}, :B{instr.true.id}"
                )
                lines.append(
                    f"    goto :B{instr.false.id}"
                )
            elif name == "DPackedSwitch":
                r = reg_map[instr.cond]
                payload_label = f":pswitch_data_{switch_payload_idx}"
                switch_payload_idx += 1
                lines.append(f"    packed-switch {r}, {payload_label}")
                lines.append(f"    goto :B{instr.default.id}")
                payload = [f"  {payload_label}", f"    .packed-switch {instr.first_key}"]
                for target in instr.targets:
                    payload.append(f"        :B{target.id}")
                payload.append("    .end packed-switch")
                switch_payloads.extend(payload)
            elif name == "DSparseSwitch":
                if instr.keys != sorted(instr.keys):
                    raise RuntimeError("sparse-switch keys must be sorted ascending")
                if len(set(instr.keys)) != len(instr.keys):
                    raise RuntimeError("sparse-switch keys must be unique")
                if len(instr.keys) != len(instr.targets):
                    raise RuntimeError("sparse-switch keys/targets length mismatch")
                r = reg_map[instr.cond]
                payload_label = f":sswitch_data_{switch_payload_idx}"
                switch_payload_idx += 1
                lines.append(f"    sparse-switch {r}, {payload_label}")
                lines.append(f"    goto :B{instr.default.id}")
                payload = [f"  {payload_label}", "    .sparse-switch"]
                for key, target in zip(instr.keys, instr.targets):
                    payload.append(f"        {int(key)} -> :B{target.id}")
                payload.append("    .end sparse-switch")
                switch_payloads.extend(payload)

            elif name == "DInvoke":
                invoke = {
                    "static": "invoke-static",
                    "virtual": "invoke-virtual",
                    "direct": "invoke-direct",
                    "super": "invoke-super",
                    "interface": "invoke-interface",
                }.get(instr.invoke_kind)
                if invoke is None:
                    raise RuntimeError(
                        f"Unsupported invoke kind: {instr.invoke_kind}"
                    )

                arg_types = instr.arg_types or [None] * len(instr.args)
                if instr.invoke_kind in ("virtual", "direct", "interface", "super"):
                    if len(arg_types) == len(instr.args):
                        arg_types = arg_types[1:]
                    elif len(arg_types) != len(instr.args) - 1:
                        raise RuntimeError(
                            "Call arg_types length does not match args for instance invoke"
                        )
                elif len(arg_types) != len(instr.args):
                    raise RuntimeError(
                        "Call arg_types length does not match args"
                    )

                def _type_desc(t):
                    from ir.types import AhnaliType
                    if isinstance(t, str):
                        if len(t) == 1:
                            return t
                        return t
                    if t is None:
                        raise RuntimeError("Call arg type missing")
                    if t == AhnaliType.INT:
                        return "I"
                    if t == AhnaliType.FLOAT:
                        return "F"
                    if t == AhnaliType.BOOL:
                        return "Z"
                    if t == AhnaliType.STRING:
                        return "Ljava/lang/String;"
                    if t == AhnaliType.OBJECT:
                        return "Ljava/lang/Object;"
                    raise RuntimeError(f"Unsupported type {t}")

                arg_desc = "".join(_type_desc(t) for t in arg_types)

                from ir.types import AhnaliType
                if instr.return_type is None:
                    ret_desc = "V"
                elif instr.return_type == AhnaliType.INT:
                    ret_desc = "I"
                elif instr.return_type == AhnaliType.FLOAT:
                    ret_desc = "F"
                elif instr.return_type == AhnaliType.BOOL:
                    ret_desc = "Z"
                elif instr.return_type == AhnaliType.STRING:
                    ret_desc = "Ljava/lang/String;"
                elif instr.return_type == AhnaliType.OBJECT:
                    ret_desc = "Ljava/lang/Object;"
                elif isinstance(instr.return_type, str):
                    ret_desc = instr.return_type
                else:
                    raise RuntimeError(f"Unsupported return type {instr.return_type}")

                regs = ", ".join(reg_map[a.ssa] for a in instr.args)
                lines.append(
                    f"    {invoke} {{{regs}}}, {instr.owner}->{instr.method}({arg_desc}){ret_desc}"
                )

                if instr.dst and instr.return_type is not None:
                    rd = reg_map[instr.dst.ssa]
                    if instr.return_type in ("J", "D"):
                        lines.append(f"    move-result-wide {rd}")
                    elif (
                        instr.return_type == AhnaliType.OBJECT
                        or instr.return_type == AhnaliType.STRING
                        or (isinstance(instr.return_type, str) and instr.return_type.startswith("L"))
                    ):
                        lines.append(f"    move-result-object {rd}")
                    else:
                        lines.append(f"    move-result {rd}")
            elif name == "DInstanceOf":
                rd = reg_map[instr.dst]
                ro = reg_map[instr.obj]
                lines.append(f"    instance-of {rd}, {ro}, {instr.desc}")

            elif name == "DReturnVoid":
                pass  # ignore inner return

    if switch_payloads:
        lines.append("")
        lines.extend(switch_payloads)

    lines.append("")
    lines.append("    return-void")
    lines.append(".end method")

    return "\n".join(lines)


def emit_activity_wrapper_smali(
    activity_desc: str = "Lcom/ahnali/preview/MainActivity;",
    target_desc: str = "LTest;",
    target_sig: str = "()V",
    emit_system_back_bridge: bool = False,
    back_sig: str = "()I",
    back_method: str = "onSystemBack",
):
    lines = []

    lines.append(f".class public {activity_desc}")
    lines.append(".super Landroid/app/Activity;")
    lines.append("")

    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 1")
    lines.append("    invoke-direct {p0}, Landroid/app/Activity;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    lines.append(".method protected onCreate(Landroid/os/Bundle;)V")
    lines.append("    .locals 0")
    lines.append("    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V")
    if target_sig.startswith("()"):
        lines.append(f"    invoke-static {{}}, {target_desc}->main{target_sig}")
    else:
        lines.append(f"    invoke-static {{p0}}, {target_desc}->main{target_sig}")
    lines.append("    return-void")
    lines.append(".end method")
    if emit_system_back_bridge:
        lines.append("")
        lines.append(".method public onBackPressed()V")
        lines.append("    .locals 1")
        lines.append(f"    invoke-static {{}}, {target_desc}->{back_method}{back_sig}")
        lines.append("    move-result v0")
        lines.append("    if-eqz v0, :ahnali_call_super")
        lines.append("    return-void")
        lines.append("  :ahnali_call_super")
        lines.append("    invoke-super {p0}, Landroid/app/Activity;->onBackPressed()V")
        lines.append("    return-void")
        lines.append(".end method")

    return "\n".join(lines)


def emit_list_view_adapter_smali(
    class_desc: str,
    *,
    item_layout_res: int = 0x1090003,
):
    lines = []
    lines.append(f".class public {class_desc}")
    lines.append(".super Landroid/widget/BaseAdapter;")
    lines.append("")
    lines.append(".field private final mInflater:Landroid/view/LayoutInflater;")
    lines.append(".field private final mItems:[Ljava/lang/String;")
    lines.append("")

    lines.append(".method public constructor <init>(Landroid/content/Context;[Ljava/lang/String;)V")
    lines.append("    .locals 1")
    lines.append("    invoke-direct {p0}, Landroid/widget/BaseAdapter;-><init>()V")
    lines.append("    iput-object p2, p0, " + class_desc + "->mItems:[Ljava/lang/String;")
    lines.append(
        "    invoke-static {p1}, Landroid/view/LayoutInflater;->from(Landroid/content/Context;)Landroid/view/LayoutInflater;"
    )
    lines.append("    move-result-object v0")
    lines.append("    iput-object v0, p0, " + class_desc + "->mInflater:Landroid/view/LayoutInflater;")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    lines.append(".method public getCount()I")
    lines.append("    .locals 1")
    lines.append("    iget-object v0, p0, " + class_desc + "->mItems:[Ljava/lang/String;")
    lines.append("    array-length v0, v0")
    lines.append("    return v0")
    lines.append(".end method")
    lines.append("")

    lines.append(".method public getItem(I)Ljava/lang/Object;")
    lines.append("    .locals 1")
    lines.append("    iget-object v0, p0, " + class_desc + "->mItems:[Ljava/lang/String;")
    lines.append("    aget-object v0, v0, p1")
    lines.append("    return-object v0")
    lines.append(".end method")
    lines.append("")

    lines.append(".method public getItemId(I)J")
    lines.append("    .locals 2")
    lines.append("    int-to-long v0, p1")
    lines.append("    return-wide v0")
    lines.append(".end method")
    lines.append("")

    lines.append(".method public getView(ILandroid/view/View;Landroid/view/ViewGroup;)Landroid/view/View;")
    lines.append("    .locals 6")
    lines.append("    if-nez p2, :reuse_view")
    lines.append("    iget-object v0, p0, " + class_desc + "->mInflater:Landroid/view/LayoutInflater;")
    lines.append(f"    const v1, 0x{item_layout_res:x}")
    lines.append("    const/4 v2, 0x0")
    lines.append(
        "    invoke-virtual {v0, v1, p3, v2}, Landroid/view/LayoutInflater;->inflate(ILandroid/view/ViewGroup;Z)Landroid/view/View;"
    )
    lines.append("    move-result-object p2")
    lines.append("    const v1, 0x1020014")
    lines.append("    invoke-virtual {p2, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;")
    lines.append("    move-result-object v3")
    lines.append("    check-cast v3, Landroid/widget/TextView;")
    lines.append("    invoke-virtual {p2, v3}, Landroid/view/View;->setTag(Ljava/lang/Object;)V")
    lines.append("    goto :bind")
    lines.append("")
    lines.append("  :reuse_view")
    lines.append("    nop")
    lines.append("")
    lines.append("  :bind")
    lines.append("    invoke-virtual {p2}, Landroid/view/View;->getTag()Ljava/lang/Object;")
    lines.append("    move-result-object v4")
    lines.append("    check-cast v4, Landroid/widget/TextView;")
    lines.append("    iget-object v5, p0, " + class_desc + "->mItems:[Ljava/lang/String;")
    lines.append("    aget-object v5, v5, p1")
    lines.append("    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V")
    lines.append("    return-object p2")
    lines.append(".end method")
    return "\n".join(lines)


def emit_ui_runnable_click_smali(
    class_desc: str,
    target_desc: str,
    target_method: str,
):
    lines = []
    lines.append(f".class public {class_desc}")
    lines.append(".super Ljava/lang/Object;")
    lines.append(".implements Ljava/lang/Runnable;")
    lines.append("")
    lines.append(".field private final mView:Landroid/view/View;")
    lines.append("")
    lines.append(".method public constructor <init>(Landroid/view/View;)V")
    lines.append("    .locals 0")
    lines.append("    invoke-direct {p0}, Ljava/lang/Object;-><init>()V")
    lines.append(f"    iput-object p1, p0, {class_desc}->mView:Landroid/view/View;")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")
    lines.append(".method public run()V")
    lines.append("    .locals 1")
    lines.append(f"    iget-object v0, p0, {class_desc}->mView:Landroid/view/View;")
    lines.append(f"    invoke-static {{v0}}, {target_desc}->{target_method}(Landroid/view/View;)V")
    lines.append("    return-void")
    lines.append(".end method")
    return "\n".join(lines)


def emit_http_route_async_worker_smali(class_desc: str):
    lines = []
    lines.append(f".class public {class_desc}")
    lines.append(".super Ljava/lang/Object;")
    lines.append(".implements Ljava/lang/Runnable;")
    lines.append("")
    lines.append(".field private final mCtx:Landroid/app/Activity;")
    lines.append(".field private final mUrl:Ljava/lang/String;")
    lines.append(".field private final mFallback:Ljava/lang/String;")
    lines.append(".field private final mMethod:Ljava/lang/String;")
    lines.append(".field private final mHeaders:Ljava/lang/String;")
    lines.append(".field private final mBody:Ljava/lang/String;")
    lines.append(".field private final mOnSuccess:Ljava/lang/Runnable;")
    lines.append(".field private final mOnFailure:Ljava/lang/Runnable;")
    lines.append(".field private final mOnProgress:Ljava/lang/Runnable;")
    lines.append(".field private final mToken:I")
    lines.append(".field private final mRetries:I")
    lines.append(".field private final mTimeoutMs:I")
    lines.append("")
    lines.append(
        ".method public constructor <init>(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/Runnable;Ljava/lang/Runnable;III)V"
    )
    lines.append("    .locals 0")
    lines.append("    invoke-direct {p0}, Ljava/lang/Object;-><init>()V")
    lines.append(f"    iput-object p1, p0, {class_desc}->mCtx:Landroid/app/Activity;")
    lines.append(f"    iput-object p2, p0, {class_desc}->mUrl:Ljava/lang/String;")
    lines.append(f"    iput-object p3, p0, {class_desc}->mFallback:Ljava/lang/String;")
    lines.append(f"    iput-object p4, p0, {class_desc}->mMethod:Ljava/lang/String;")
    lines.append(f"    iput-object p5, p0, {class_desc}->mHeaders:Ljava/lang/String;")
    lines.append(f"    iput-object p6, p0, {class_desc}->mBody:Ljava/lang/String;")
    lines.append(f"    iput-object p7, p0, {class_desc}->mOnSuccess:Ljava/lang/Runnable;")
    lines.append(f"    iput-object p8, p0, {class_desc}->mOnFailure:Ljava/lang/Runnable;")
    lines.append(f"    iput-object p9, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append(f"    iput p10, p0, {class_desc}->mToken:I")
    lines.append(f"    iput p11, p0, {class_desc}->mRetries:I")
    lines.append(f"    iput p12, p0, {class_desc}->mTimeoutMs:I")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")
    lines.append(".method public run()V")
    lines.append("    .locals 11")
    lines.append(f"    iget-object v0, p0, {class_desc}->mCtx:Landroid/app/Activity;")
    lines.append(f"    iget v1, p0, {class_desc}->mToken:I")
    lines.append("    const/4 v2, 0x5")
    lines.append("    invoke-static {v1, v2}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V")
    lines.append("    if-eqz v0, :ahnali_async_try_start")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_try_start")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    :ahnali_async_try_start")
    lines.append("    invoke-static {v1}, Lcom/ahnali/runtime/HttpHelper;->shouldCancel(I)I")
    lines.append("    move-result v2")
    lines.append("    if-eqz v2, :ahnali_async_check_input")
    lines.append("    const/4 v7, 0x7")
    lines.append("    const/4 v8, -0x1")
    lines.append(f"    iget-object v9, p0, {class_desc}->mFallback:Ljava/lang/String;")
    lines.append("    goto :ahnali_async_fail_finalize")
    lines.append("    :ahnali_async_check_input")
    lines.append("    if-eqz v0, :ahnali_async_invalid_input")
    lines.append(f"    iget-object v4, p0, {class_desc}->mUrl:Ljava/lang/String;")
    lines.append("    if-eqz v4, :ahnali_async_invalid_input")
    lines.append(f"    iget-object v9, p0, {class_desc}->mFallback:Ljava/lang/String;")
    lines.append(f"    iget v5, p0, {class_desc}->mRetries:I")
    lines.append("    if-gez v5, :ahnali_async_retries_ready")
    lines.append("    const/4 v5, 0x0")
    lines.append("    :ahnali_async_retries_ready")
    lines.append("    add-int/lit8 v5, v5, 0x1")
    lines.append("    const/4 v6, 0x0")
    lines.append("    const/4 v7, 0x1")
    lines.append("    const/4 v8, -0x1")
    lines.append("    :ahnali_async_attempt_loop")
    lines.append("    invoke-static {v1}, Lcom/ahnali/runtime/HttpHelper;->shouldCancel(I)I")
    lines.append("    move-result v2")
    lines.append("    if-eqz v2, :ahnali_async_attempt_call")
    lines.append("    const/4 v7, 0x7")
    lines.append("    goto :ahnali_async_fail_finalize")
    lines.append("    :ahnali_async_attempt_call")
    lines.append(f"    iget-object v10, p0, {class_desc}->mMethod:Ljava/lang/String;")
    lines.append(f"    iget-object v3, p0, {class_desc}->mHeaders:Ljava/lang/String;")
    lines.append(f"    iget-object v2, p0, {class_desc}->mBody:Ljava/lang/String;")
    lines.append(f"    iget v7, p0, {class_desc}->mTimeoutMs:I")
    lines.append(
        "    invoke-static {v0, v4, v10, v3, v2, v7}, Lcom/ahnali/runtime/HttpHelper;->httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I"
    )
    lines.append("    move-result v8")
    lines.append(
        "    invoke-static {v0, v4, v10, v3, v2, v9, v7}, Lcom/ahnali/runtime/HttpHelper;->httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;"
    )
    lines.append("    move-result-object v9")
    lines.append(
        "    invoke-static {v0, v4, v10, v3, v2, v7}, Lcom/ahnali/runtime/HttpHelper;->httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I"
    )
    lines.append("    move-result v7")
    lines.append("    invoke-static {v1}, Lcom/ahnali/runtime/HttpHelper;->shouldCancel(I)I")
    lines.append("    move-result v2")
    lines.append("    if-eqz v2, :ahnali_async_cancel_checked")
    lines.append("    const/4 v7, 0x7")
    lines.append("    :ahnali_async_cancel_checked")
    lines.append("    const/16 v3, 0xc8")
    lines.append("    if-ne v8, v3, :ahnali_async_retry_or_fail")
    lines.append("    if-nez v7, :ahnali_async_retry_or_fail")
    lines.append("    const/4 v3, 0x0")
    lines.append("    invoke-static {v1, v3}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V")
    lines.append("    invoke-static {v1, v8}, Lcom/ahnali/runtime/HttpHelper;->setAsyncStatus(II)V")
    lines.append("    invoke-static {v1, v9}, Lcom/ahnali/runtime/HttpHelper;->setAsyncBody(ILjava/lang/String;)V")
    lines.append("    const/16 v3, 0x64")
    lines.append("    invoke-static {v1, v3}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V")
    lines.append("    if-eqz v0, :ahnali_async_return")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_post_success")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    :ahnali_async_post_success")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnSuccess:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_return")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    goto :ahnali_async_return")
    lines.append("    :ahnali_async_retry_or_fail")
    lines.append("    add-int/lit8 v6, v6, 0x1")
    lines.append("    if-ge v6, v5, :ahnali_async_fail_finalize")
    lines.append("    mul-int/lit8 v2, v6, 0x50")
    lines.append("    div-int/2addr v2, v5")
    lines.append("    add-int/lit8 v2, v2, 0xa")
    lines.append("    invoke-static {v1, v2}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V")
    lines.append("    if-eqz v0, :ahnali_async_attempt_loop")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_attempt_loop")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    goto :ahnali_async_attempt_loop")
    lines.append("    :ahnali_async_try_end")
    lines.append(
        "    .catch Ljava/lang/Exception; {:ahnali_async_try_start .. :ahnali_async_try_end} :ahnali_async_catch"
    )
    lines.append("    :ahnali_async_invalid_input")
    lines.append("    const/4 v7, 0x1")
    lines.append("    const/4 v8, -0x1")
    lines.append(f"    iget-object v9, p0, {class_desc}->mFallback:Ljava/lang/String;")
    lines.append("    :ahnali_async_fail_finalize")
    lines.append("    invoke-static {v1, v7}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V")
    lines.append("    invoke-static {v1, v8}, Lcom/ahnali/runtime/HttpHelper;->setAsyncStatus(II)V")
    lines.append("    invoke-static {v1, v9}, Lcom/ahnali/runtime/HttpHelper;->setAsyncBody(ILjava/lang/String;)V")
    lines.append("    const/16 v2, 0x64")
    lines.append("    invoke-static {v1, v2}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V")
    lines.append("    if-eqz v0, :ahnali_async_return")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_fail_post")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    :ahnali_async_fail_post")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnFailure:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_return")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    goto :ahnali_async_return")
    lines.append("    :ahnali_async_catch")
    lines.append("    const/4 v7, 0x2")
    lines.append("    const/4 v8, -0x1")
    lines.append(f"    iget-object v9, p0, {class_desc}->mFallback:Ljava/lang/String;")
    lines.append("    invoke-static {v1, v7}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V")
    lines.append("    invoke-static {v1, v8}, Lcom/ahnali/runtime/HttpHelper;->setAsyncStatus(II)V")
    lines.append("    invoke-static {v1, v9}, Lcom/ahnali/runtime/HttpHelper;->setAsyncBody(ILjava/lang/String;)V")
    lines.append("    const/16 v2, 0x64")
    lines.append("    invoke-static {v1, v2}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V")
    lines.append(f"    iget-object v0, p0, {class_desc}->mCtx:Landroid/app/Activity;")
    lines.append("    if-eqz v0, :ahnali_async_return")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnProgress:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_catch_fail")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    :ahnali_async_catch_fail")
    lines.append(f"    iget-object v3, p0, {class_desc}->mOnFailure:Ljava/lang/Runnable;")
    lines.append("    if-eqz v3, :ahnali_async_return")
    lines.append("    invoke-virtual {v0, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V")
    lines.append("    :ahnali_async_return")
    lines.append("    return-void")
    lines.append(".end method")
    return "\n".join(lines)


def emit_event_listener_smali(
    class_desc: str,
    target_desc: str,
    target_method: str,
    listener_kind: str = "click",
):
    kind = str(listener_kind or "click").strip().lower()
    if kind == "list_adapter":
        item_layout_res = 0x1090003
        try:
            item_layout_res = int(str(target_method), 0)
        except Exception:
            item_layout_res = 0x1090003
        return emit_list_view_adapter_smali(
            class_desc=class_desc,
            item_layout_res=item_layout_res,
        )
    if kind == "ui_runnable_click":
        return emit_ui_runnable_click_smali(
            class_desc=class_desc,
            target_desc=target_desc,
            target_method=target_method,
        )
    if kind == "http_route_async_worker":
        return emit_http_route_async_worker_smali(class_desc=class_desc)

    lines = []

    lines.append(f".class public {class_desc}")
    lines.append(".super Ljava/lang/Object;")

    if kind == "click":
        iface = "Landroid/view/View$OnClickListener;"
    elif kind == "long_click":
        iface = "Landroid/view/View$OnLongClickListener;"
    elif kind in {
        "touch",
        "double_tap",
        "swipe",
        "scroll",
        "fling",
        "pinch",
        "zoom",
        "rotate_gesture",
        "scale_gesture_detector",
    }:
        iface = "Landroid/view/View$OnTouchListener;"
    elif kind in {"drag", "drop"}:
        iface = "Landroid/view/View$OnDragListener;"
    elif kind == "editor_action":
        iface = "Landroid/widget/TextView$OnEditorActionListener;"
    elif kind == "key":
        iface = "Landroid/view/View$OnKeyListener;"
    elif kind == "change":
        iface = "Landroid/widget/CompoundButton$OnCheckedChangeListener;"
    elif kind == "slider_change":
        iface = "Landroid/widget/SeekBar$OnSeekBarChangeListener;"
    elif kind == "radiogroup_change":
        iface = "Landroid/widget/RadioGroup$OnCheckedChangeListener;"
    elif kind == "text_change":
        iface = "Landroid/text/TextWatcher;"
    elif kind == "item_selected":
        iface = "Landroid/widget/AdapterView$OnItemSelectedListener;"
    elif kind == "focus_change":
        iface = "Landroid/view/View$OnFocusChangeListener;"
    elif kind == "menu_item_selected":
        iface = "Landroid/widget/PopupMenu$OnMenuItemClickListener;"
    else:
        raise RuntimeError(f"Unsupported listener kind: {listener_kind}")

    lines.append(f".implements {iface}")
    lines.append("")

    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 0")
    lines.append("    invoke-direct {p0}, Ljava/lang/Object;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    if kind == "click":
        lines.append(".method public onClick(Landroid/view/View;)V")
        lines.append("    .locals 0")
        lines.append(f"    invoke-static {{p1}}, {target_desc}->{target_method}(Landroid/view/View;)V")
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "long_click":
        lines.append(".method public onLongClick(Landroid/view/View;)Z")
        lines.append("    .locals 1")
        lines.append(f"    invoke-static {{p1}}, {target_desc}->{target_method}(Landroid/view/View;)V")
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")
    elif kind in {
        "touch",
        "double_tap",
        "swipe",
        "scroll",
        "fling",
        "pinch",
        "zoom",
        "rotate_gesture",
        "scale_gesture_detector",
    }:
        lines.append(".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z")
        lines.append("    .locals 1")
        lines.append(
            f"    invoke-static {{p1, p2}}, {target_desc}->{target_method}(Landroid/view/View;Landroid/view/MotionEvent;)V"
        )
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")
    elif kind in {"drag", "drop"}:
        lines.append(".method public onDrag(Landroid/view/View;Landroid/view/DragEvent;)Z")
        lines.append("    .locals 1")
        lines.append(
            f"    invoke-static {{p1, p2}}, {target_desc}->{target_method}(Landroid/view/View;Landroid/view/DragEvent;)V"
        )
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")
    elif kind == "editor_action":
        lines.append(".method public onEditorAction(Landroid/widget/TextView;ILandroid/view/KeyEvent;)Z")
        lines.append("    .locals 1")
        lines.append(
            f"    invoke-static {{p1, p2, p3}}, {target_desc}->{target_method}(Landroid/widget/TextView;ILandroid/view/KeyEvent;)V"
        )
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")
    elif kind == "key":
        lines.append(".method public onKey(Landroid/view/View;ILandroid/view/KeyEvent;)Z")
        lines.append("    .locals 1")
        lines.append(
            f"    invoke-static {{p1, p2, p3}}, {target_desc}->{target_method}(Landroid/view/View;ILandroid/view/KeyEvent;)V"
        )
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")
    elif kind == "change":
        lines.append(".method public onCheckedChanged(Landroid/widget/CompoundButton;Z)V")
        lines.append("    .locals 0")
        lines.append(
            f"    invoke-static {{p1, p2}}, {target_desc}->{target_method}(Landroid/widget/CompoundButton;Z)V"
        )
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "slider_change":
        lines.append(".method public onProgressChanged(Landroid/widget/SeekBar;IZ)V")
        lines.append("    .locals 0")
        lines.append(
            f"    invoke-static {{p1, p2, p3}}, {target_desc}->{target_method}(Landroid/widget/SeekBar;IZ)V"
        )
        lines.append("    return-void")
        lines.append(".end method")
        lines.append("")
        lines.append(".method public onStartTrackingTouch(Landroid/widget/SeekBar;)V")
        lines.append("    .locals 0")
        lines.append("    return-void")
        lines.append(".end method")
        lines.append("")
        lines.append(".method public onStopTrackingTouch(Landroid/widget/SeekBar;)V")
        lines.append("    .locals 0")
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "radiogroup_change":
        lines.append(".method public onCheckedChanged(Landroid/widget/RadioGroup;I)V")
        lines.append("    .locals 0")
        lines.append(
            f"    invoke-static {{p1, p2}}, {target_desc}->{target_method}(Landroid/widget/RadioGroup;I)V"
        )
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "text_change":
        lines.append(".method public beforeTextChanged(Ljava/lang/CharSequence;III)V")
        lines.append("    .locals 0")
        lines.append("    return-void")
        lines.append(".end method")
        lines.append("")
        lines.append(".method public onTextChanged(Ljava/lang/CharSequence;III)V")
        lines.append("    .locals 0")
        lines.append("    return-void")
        lines.append(".end method")
        lines.append("")
        lines.append(".method public afterTextChanged(Landroid/text/Editable;)V")
        lines.append("    .locals 0")
        lines.append(f"    invoke-static {{p1}}, {target_desc}->{target_method}(Landroid/text/Editable;)V")
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "item_selected":
        lines.append(".method public onItemSelected(Landroid/widget/AdapterView;Landroid/view/View;IJ)V")
        lines.append("    .locals 0")
        lines.append(
            f"    invoke-static {{p1, p2, p3, p4, p5}}, {target_desc}->{target_method}(Landroid/widget/AdapterView;Landroid/view/View;IJ)V"
        )
        lines.append("    return-void")
        lines.append(".end method")
        lines.append("")
        lines.append(".method public onNothingSelected(Landroid/widget/AdapterView;)V")
        lines.append("    .locals 0")
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "focus_change":
        lines.append(".method public onFocusChange(Landroid/view/View;Z)V")
        lines.append("    .locals 0")
        lines.append(f"    invoke-static {{p1, p2}}, {target_desc}->{target_method}(Landroid/view/View;Z)V")
        lines.append("    return-void")
        lines.append(".end method")
    elif kind == "menu_item_selected":
        lines.append(".method public onMenuItemClick(Landroid/view/MenuItem;)Z")
        lines.append("    .locals 1")
        lines.append(f"    invoke-static {{p1}}, {target_desc}->{target_method}(Landroid/view/MenuItem;)V")
        lines.append("    const/4 v0, 0x1")
        lines.append("    return v0")
        lines.append(".end method")

    return "\n".join(lines)


def emit_click_listener_smali(
    class_desc: str = "Lcom/ahnali/preview/AhnaliClickListener;",
    target_desc: str = "LTest;",
    target_method: str = "onClick",
):
    return emit_event_listener_smali(
        class_desc=class_desc,
        target_desc=target_desc,
        target_method=target_method,
        listener_kind="click",
    )
