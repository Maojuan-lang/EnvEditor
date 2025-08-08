import re
import tkinter as tk
from tkinter import ttk

ENV_FILE = "config.env"  # 改成你的 env 路径

class ToolTip:
    """简单鼠标悬停提示"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1, font=("Arial", 10), justify="left")
        label.pack(ipadx=5, ipady=3)
        self.tip_window = tw

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def parse_env_file():
    """解析 env 文件，返回 items 列表和原始所有行"""
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]
    except FileNotFoundError:
        lines = []

    items = []
    i = 0
    N = len(lines)
    while i < N:
        line = lines[i].strip()
        # 跳过文件级别注释或无关行
        if not line:
            i += 1
            continue
        if line.startswith("##"):
            i += 1
            continue

        # 找到 type 标记
        if line.lower().startswith("# type:"):
            # 读取 type
            try:
                control_type = int(line.split(":", 1)[1].strip())
            except Exception:
                i += 1
                continue
            i += 1

            # 收集后续的 # 注释块（跳过 ##），直到遇到非注释非空白行
            comment_lines = []
            while i < N:
                l = lines[i]
                if not l.strip():
                    i += 1
                    continue
                if not l.strip().startswith("#"):
                    break
                if l.strip().startswith("##"):
                    i += 1
                    continue
                text = l.lstrip("#").strip()
                comment_lines.append(text)
                i += 1

            # 在 comment_lines 中寻找 value: 行（可能没有）
            options = None
            value_idx = None
            for idx, txt in enumerate(comment_lines):
                if txt.lower().startswith("value:"):
                    value_idx = idx
                    # 解析 value: 后面的部分，用 '.' 分割，忽略空项
                    valpart = txt.split(":", 1)[1].strip()
                    options = [s for s in (v.strip() for v in valpart.split(".")) if s != ""]
                    break
            if value_idx is not None:
                # 从 comment_lines 中移除 value: 行（它不是 label/tooltip）
                comment_lines.pop(value_idx)

            # label 取 comment_lines 的最后一行（如果存在），其余为 tooltip（保持原顺序）
            if comment_lines:
                label = comment_lines[-1]
                tooltip_lines = comment_lines[:-1]
            else:
                label = ""
                tooltip_lines = []

            # 跳过可能的空行，寻找 key=value
            while i < N and not lines[i].strip():
                i += 1

            if i < N and "=" in lines[i] and not lines[i].strip().startswith("#"):
                kline = lines[i].strip()
                key, val = kline.split("=", 1)
                items.append({
                    "type": control_type,
                    "label": label,
                    "tooltip": "\n".join(tooltip_lines).strip(),
                    "key": key.strip(),
                    "value": val.strip(),
                    "options": options  # 下拉选项或 None
                })
                i += 1
            else:
                # 没找到 key=value，跳过继续
                continue
        else:
            i += 1

    return items, lines

def save_item_to_file(item):
    if item['type']==1 or item['type']==2:
        """把单个 item 的值写回 env 文件（替换匹配到的 key= 行，找不到则追加）"""
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        except FileNotFoundError:
            lines = []

        pattern = re.compile(r'^\s*' + re.escape(item['key']) + r'\s*=')
        replaced = False
        text_value_map = {}
        opts = item['options']
        if opts:
            for i in range(0, len(opts), 2):
                value = opts[i]
                text = opts[i + 1]
                text_value_map[text] = value
        for idx, ln in enumerate(lines):
            if pattern.match(ln):
                if text_value_map:
                    lines[idx] = f"{item['key']}={text_value_map[item['value']]}"
                else:
                    lines[idx] = f"{item['key']}={item['value']}"
                replaced = True
                break
        if not replaced:
            # 如果没有找到对应的 key，则追加到文件末尾（保留换行格式）
            if lines and lines[-1].strip() != "":
                lines.append("")  # 保持分段
            if text_value_map:
                lines.append(f"{item['key']}={text_value_map[item['value']]}")
            else:
                lines.append(f"{item['key']}={item['value']}")

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    if item['type']==3:
        """把单个 item 的值写回 env 文件（替换匹配到的 key= 行，找不到则追加）"""
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        except FileNotFoundError:
            lines = []

        pattern = re.compile(r'^\s*' + re.escape(item['key']) + r'\s*=')
        replaced = False
        for idx, ln in enumerate(lines):
            if pattern.match(ln):
                lines[idx] = f"{item['key']}={item['value']}"
                replaced = True
                break
        if not replaced:
            # 如果没有找到对应的 key，则追加到文件末尾（保留换行格式）
            if lines and lines[-1].strip() != "":
                lines.append("")  # 保持分段
            lines[idx] = f"{item['key']}={item['value']}"
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    if item['type'] == 5:
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        except FileNotFoundError:
            lines = []

        pattern = re.compile(r'^\s*' + re.escape(item['key']) + r'\s*=')
        replaced = False
        for idx, ln in enumerate(lines):
            if pattern.match(ln):
                lines[idx] = f"{item['key']}={item['value']}"
                replaced = True
                break
        if not replaced:
            # 如果没有找到对应的 key，则追加到文件末尾（保留换行格式）
            if lines and lines[-1].strip() != "":
                lines.append("")  # 保持分段
            lines[idx] = f"{item['key']}={item['value']}"
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

def center_window(root):
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

def on_multi_check(item, vars_list):
    selected = [val for var, val in vars_list if var.get() == 1]
    if not selected:
        selected = [vars_list[0][1]]  # 默认第一个
    item['value'] = ".".join(selected)
    save_item_to_file(item)

def create_gui():
    root = tk.Tk()
    root.title("Env 配置编辑器")
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    items, _orig = parse_env_file()

    def on_check(var, item):
        # var 是 IntVar
        item['value'] = str(int(var.get()))
        save_item_to_file(item)

    def on_combo_change(event, var, item):
        item['value'] = var.get()
        save_item_to_file(item)

    # 如果没有解析到任何项，显示提示
    if not items:
        frame = ttk.Frame()
        frame.pack(padx=24, pady=6, fill="x")
        lbl = ttk.Label(frame, text="未解析到可编辑项（检查 env 格式）")
        lbl.pack(padx=10, pady=10)
    else:
        for item in items:
            # ---------------- type:4 分组 ----------------
            if item['type'] == 4:
                current_tab = ttk.Frame(notebook)
                style = ttk.Style()
                style.theme_use("default")  # 先用默认主题
                style.configure("TNotebook.Tab", background="#ffe6e6")  # 标签背景淡红
                style.map("TNotebook.Tab", background=[("selected", "#ff8080")])  # 选中时稍深
                notebook.add(current_tab, text=item['label'] or item['key'])
                continue

            if not current_tab:
                current_tab = ttk.Frame(notebook)
                notebook.add(current_tab, text="默认")

            frame = ttk.Frame(current_tab)
            frame.pack(anchor="w", pady=6, padx=12, fill="x")

            # ---------------- type:1 单选框 ----------------
            if item['type'] == 1:
                lbl = ttk.Label(frame, text=item['label'] or item['key'])
                lbl.pack(side="left", padx=(0, 6))
                var = tk.IntVar(value=int(item.get('value', 0)))
                cb = ttk.Checkbutton(frame, variable=var,
                                     command=lambda v=var, it=item: on_check(v, it))
                cb.pack(side="left")
                if item.get('tooltip'):
                    ToolTip(cb, item['tooltip'])

            # ---------------- type:2 下拉框 ----------------
            elif item['type'] == 2:
                lbl = ttk.Label(frame, text=item['label'] or item['key'])
                lbl.pack(side="left", padx=(0, 6))
                opts = item.get('options') or []
                value_text_map = {}
                for i in range(0, len(opts), 2):
                    value = opts[i]
                    text = opts[i + 1]
                    value_text_map[value] = text
                label_text = list(value_text_map.values())
                var = tk.StringVar(value=value_text_map.get(item['value'], ""))
                combo = ttk.Combobox(frame, textvariable=var, values=label_text, state="readonly")
                combo.pack(side="left")
                combo.bind("<<ComboboxSelected>>",
                           lambda e, v=var, it=item: on_combo_change(e, v, it))
                if item.get('tooltip'):
                    ToolTip(combo, item['tooltip'])

            # ---------------- type:3 多选框 ----------------
            elif item['type'] == 3:
                lbl = ttk.Label(frame, text=item['label'] or item['key'])
                lbl.pack(side="left", padx=(0, 6))
                opts = item.get('options') or []
                values = [opts[i] for i in range(0, len(opts), 2)]
                texts = [opts[i] for i in range(1, len(opts), 2)]
                vars_list = []
                for val, text in zip(values, texts):
                    var = tk.IntVar(value=1 if val in item['value'].split(".") else 0)
                    vars_list.append((var, val))
                    cb = ttk.Checkbutton(frame, text=text, variable=var,
                                         command=lambda it=item, vlist=vars_list: on_multi_check(it, vlist))
                    cb.pack(side="left", padx=(6, 0))
                if item.get('tooltip'):
                    ToolTip(frame, item['tooltip'])
            elif item['type'] == 5:
                opts = item.get('options', [])
                value_text_map = {}
                for i in range(0, len(opts), 2):
                    if i + 1 < len(opts):
                        sid = str(opts[i]).strip()  # 确保ID是字符串
                        name = str(opts[i + 1]).strip()
                        value_text_map[sid] = name

                if not value_text_map:
                    continue

                all_ids = list(value_text_map.keys())
                all_texts = [value_text_map[i] for i in all_ids]
                # 初始化 text_to_id 映射
                text_to_id = {v: k for k, v in value_text_map.items()}
                n = len(all_ids)  # 士兵数量

                # 解析当前队伍顺序（item['value']格式："1.2.3.4"）
                current_order = item.get('value', "")
                current_ids = [s.strip() for s in current_order.split(".") if s.strip()]

                # 修正顺序：保留有效ID，补充缺失的，截断多余的
                valid_ids = [cid for cid in current_ids if cid in value_text_map]
                # 添加缺失的ID
                for sid in all_ids:
                    if sid not in valid_ids:
                        valid_ids.append(sid)
                # 确保长度一致
                current_ids = valid_ids[:n] if n > 0 else []

                # 创建容器
                outer_frame = ttk.Frame(frame)
                outer_frame.pack(anchor="w", padx=12, pady=6, fill="x")
                lbl = ttk.Label(outer_frame, text=item['label'] or item['key'])
                lbl.pack(anchor="w", pady=(0, 4))

                # 初始化 current_texts - 当前每个位置对应的士兵名称
                current_texts = [value_text_map.get(cid, "") for cid in current_ids]

                # 存储变量和下拉框
                last_texts = current_texts[:]  # 用于记录每个下拉框的上一次值
                selected_var_list = []  # 存储所有下拉框的StringVar

                def save_order(item):
                    """保存当前顺序到item['value']"""
                    selected_ids = []
                    for var in selected_var_list:
                        selected_text = var.get()
                        # 使用 text_to_id 将名称映射回ID
                        selected_ids.append(text_to_id.get(selected_text, ""))
                    item['value'] = ".".join(selected_ids)
                    save_item_to_file(item)

                def on_select(event, idx, item):
                    """下拉框选择事件处理"""
                    # 获取当前下拉框的新值
                    new_text = selected_var_list[idx].get()
                    old_text = last_texts[idx]  # 当前下拉框的旧值

                    # 检查是否有其他下拉框选择了相同的值
                    for j in range(len(selected_var_list)):
                        if j == idx:
                            continue  # 跳过自身
                        if selected_var_list[j].get() == new_text:
                            # 交换值：将重复位置的值设置为当前下拉框的旧值
                            selected_var_list[j].set(old_text)
                            last_texts[j] = old_text  # 更新记录
                            break

                    # 更新当前下拉框的记录
                    last_texts[idx] = new_text
                    save_order(item)  # 保存新顺序

                # 创建下拉框（每6个一行）
                for i in range(n):
                    if i % 6 == 0:
                        row_frame = ttk.Frame(outer_frame)
                        row_frame.pack(fill="x", pady=2)

                    # 添加序号标签 (i+1 因为序号从1开始)
                    lbl_num = ttk.Label(row_frame, text=f"{i + 1}.", width=3)
                    lbl_num.pack(side="left", padx=(0, 2))

                    # 创建并设置变量
                    selected_var = tk.StringVar(value=current_texts[i])
                    selected_var_list.append(selected_var)  # 存储变量

                    cb = ttk.Combobox(
                        row_frame,
                        textvariable=selected_var,
                        values=all_texts,
                        state="readonly",
                        width=12
                    )
                    cb.pack(side="left", padx=4)
                    cb.bind("<<ComboboxSelected>>", lambda e, idx=i,it=item: on_select(e, idx,it))

                if item.get('tooltip'):
                    ToolTip(outer_frame, item['tooltip'])

    root.update_idletasks()
    center_window(root)
    root.mainloop()

if __name__ == "__main__":

    create_gui()


