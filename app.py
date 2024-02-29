import json
import os
from functools import partial

from pywebio import *
from pywebio.output import *
from pywebio.pin import *

TYPE_MAP = {
    "float": "float",
    "str": "text",
    "int": "number",
}


class JsonEditorGUI:
    add_icon = "\U00002795"
    delete_icon = "\U0000274C"
    save_icon = "\U0001F4BE"
    refresh_icon = "\U0001F504"

    def __init__(self, config="template.json"):
        self.ext_args = None
        self.config = config
        self.configs = [f for f in os.listdir('config') if f.endswith('.json')]
        with open(f"config/{config}", 'r') as f:
            self.data = json.load(f)

    def run(self):
        session.set_env(title="Json Editor", output_animation=False)
        self.home()
        self.config_select()
        self.essential()
        self.categories()
        self.extensions()

    @use_scope("ROOT", clear=True)
    def home(self):
        put_row([
            put_scope("config_select"),
            None,
            put_tabs([
                {"title": "基本设置", "content": put_scope("essential")},
                {"title": "类别设置", "content": put_scope("categories")},
                {"title": "扩展", "content": put_scope("extensions")},
            ])
        ], size="25% 5% 70%")

    @use_scope("config_select", clear=True)
    def config_select(self):
        self.configs = [f for f in os.listdir('config') if f.endswith('.json')]
        options = [(f.split(".")[0], f) for f in self.configs]
        put_select("config", label="Config", options=options, value=self.config)

        put_buttons([self.save_icon, self.refresh_icon, self.add_icon, self.delete_icon],
                    onclick=[self.save_config, self.config_select, self.add_config, self.delete_config])

        pin_on_change("config", onchange=self.set_config, clear=True)

    @use_scope("essential", clear=True)
    def essential(self):
        unique_prefix = "_ess-"
        data_ess = self.data['essential']
        put_input(unique_prefix + "name", label="数据集名", value=data_ess['name'])
        put_input(unique_prefix + "dataset_path", label="数据集路径", value=data_ess['dataset_path'])
        put_select(unique_prefix + "dataset_type", label="数据集类型", options=[("训练集", "train"),
                                                                                ("验证集", "val"),
                                                                                ("测试集", "test")],
                   value=data_ess['dataset_type'])
        put_select(unique_prefix + "label_type", label="标签形式",
                   options=[('掩码', 'mask'), ('YOLO标注框', 'yolo_detect')], value=data_ess['label_type'])

        bg_enabled = "background" in self.data['categories']

        put_select(unique_prefix + "use_empty_background", label="背景样式",
                   options=[dict(label='纯黑背景', value=True),
                            dict(label='自定义背景' + ("" if bg_enabled else "（需要添加名为\"background\"的类别）"),
                                 value=False, disabled=not bg_enabled)],
                   value=data_ess['use_empty_background'])
        put_input(unique_prefix + "init_seed", label="初始化种子", type='number', value=data_ess['init_seed'])

        pin_on_change(unique_prefix + "name", onchange=self.set_name, clear=True)
        pin_on_change(unique_prefix + "dataset_path", onchange=self.set_dataset_path, clear=True)
        pin_on_change(unique_prefix + "dataset_type", onchange=self.set_dataset_type, clear=True)
        pin_on_change(unique_prefix + "label_type", onchange=self.set_label_type, clear=True)
        pin_on_change(unique_prefix + "use_empty_background", onchange=self.set_use_empty_background, clear=True)
        pin_on_change(unique_prefix + "init_seed", onchange=self.set_init_seed, clear=True)

    @use_scope("categories", clear=True)
    def categories(self):
        for category in self.data['categories']:
            self.category(category)
        put_button("添加类别", onclick=self.add_category)

    @use_scope("extensions", clear=True)
    def extensions(self):
        with open("extensions/arguments.json", 'r') as f:
            self.ext_args = json.load(f)
        for ext_name in self.ext_args:
            self.extension(ext_name)

    def extension(self, ext_name):
        unique_prefix = f"_ext_{ext_name}-"
        with use_scope(unique_prefix + "scope", clear=True):
            ext_arg = self.ext_args[ext_name]
            content = []
            if "description" in ext_arg:
                content.append(put_text(f"描述：{ext_arg['description']}"))
            if "entry" in ext_arg:
                content.append(put_text(f"程序入口：{ext_arg['entry']}"))
            else:
                raise ValueError(f"扩展{ext_name}缺少程序入口")

            def up_exec():
                nonlocal ext_arg
                ext_arg['exec'] = "python " + ext_arg['entry']
                for arg in ext_arg.get("args", []):
                    value = pin[unique_prefix + arg['name']]
                    if value:
                        ext_arg['exec'] += f" --{arg['name']} {pin[unique_prefix + arg['name']]}"
                # print(f"{ext_name}_exec", ext_arg['exec'])
                pin_update(unique_prefix + "_exec", value=ext_arg['exec'])

            up_exec()

            for arg in ext_arg.get("args", []):
                content.append(
                    put_input(unique_prefix + arg['name'], label=arg['name'],
                              type=TYPE_MAP.get(arg.get('type', 'text'), 'text'), placeholder=arg['help'])
                )
                pin_on_change(unique_prefix + arg['name'], onchange=lambda x: up_exec(), clear=True)

            content.append(
                put_input(unique_prefix + "_exec", label="命令行预览", value=ext_arg['exec'], readonly=True)
            )

            def exec_command():
                # print(ext_arg['exec'])
                os.system(ext_arg['exec'])
                # self.extensions()

            content.append(
                put_button("执行", onclick=exec_command)
            )

            put_collapse(ext_name, content)

    def category(self, category):
        unique_prefix = f"_cat_{category}-"
        with use_scope(unique_prefix + "scope", clear=True):
            data_cat = self.data['categories'][category]
            options_all = [f for f in os.listdir(f"{data_cat['path']}")] if data_cat['path'] else []

            def set_ops():
                new_options_all = [f for f in os.listdir(f"{data_cat['path']}")] if data_cat['path'] else []
                nonlocal options_all
                if set(options_all) != set(new_options_all):
                    options_all = new_options_all
                    pin_update(unique_prefix + "checked", options=options_all)
                return new_options_all

            set_checked = partial(self.set_category_checked, category, unique_prefix=unique_prefix, func=set_ops)

            put_row([
                put_collapse(category, [
                    put_checkbox(unique_prefix + "enabled", options=[("启用", "enabled", data_cat['enabled'])]),
                    put_input(unique_prefix + "path", label="路径", value=data_cat['path']),
                    put_input(unique_prefix + "cls", label="类别id", type='number', value=data_cat['cls']),
                    put_row([
                        put_input(unique_prefix + "min_num", label="最小数量", type='number', value=data_cat['min_num']),
                        None,
                        put_input(unique_prefix + "max_num", label="最大数量", type='number', value=data_cat['max_num']),
                        None
                    ], size="1fr 0.2fr 1fr 5fr"),
                    put_checkbox(unique_prefix + "rotate", options=[("随机旋转", "rotate", data_cat['rotate'])]),
                    put_markdown("""---
                                    子类别筛选"""),
                    # put_text("子类别"),
                    put_row([
                        put_select(unique_prefix + "checked", options=options_all,
                                   value=data_cat['checked'], multiple=True),
                        None,
                        put_button(self.refresh_icon, onclick=lambda: set_checked(data_cat['checked']))
                    ], size="88% 2% 10%"),
                    put_buttons(["全选", "全不选"], onclick=[lambda: set_checked(options_all), lambda: set_checked([])])
                ]),
                None,
                put_button(self.delete_icon, onclick=lambda: self.delete_category(category))
            ], size="88% 2% 10%")

            pin_on_change(unique_prefix + "enabled", onchange=lambda x: self.set_category_enabled(category, x), clear=True)
            pin_on_change(unique_prefix + "path", onchange=lambda x: self.set_category_path(category, x), clear=True)
            pin_on_change(unique_prefix + "cls", onchange=lambda x: self.set_category_cls(category, x), clear=True)
            pin_on_change(unique_prefix + "min_num", onchange=lambda x: self.set_category_min_max(category, min_num=x),
                          clear=True)
            pin_on_change(unique_prefix + "max_num", onchange=lambda x: self.set_category_min_max(category, max_num=x),
                          clear=True)
            pin_on_change(unique_prefix + "rotate", onchange=lambda x: self.set_category_rotate(category, x), clear=True)
            pin_on_change(unique_prefix + "checked", onchange=set_checked, clear=True)

    def set_config(self, new_config):
        self.config = new_config
        with open(f"config/{new_config}", 'r') as file:
            self.data = json.load(file)
        self.essential()
        self.categories()

    def save_config(self):
        output_file = f"config/{self.config}"
        with open(output_file, 'w') as file:
            json.dump(self.data, file, indent=2)
        toast("修改已保存", color="success")

    def add_config(self):
        def add_confirm():
            new_config = pin['new_config'] + ".json"
            copy_from_config = pin['copy_from_config']
            if new_config is None:
                toast("配置名不能为空", color="error")
                return
            if new_config in self.configs:
                toast("配置名已存在", color="error")
                return
            with open(f"config/{copy_from_config}", 'r') as file:
                data = json.load(file)
            with open(f"config/{new_config}", 'w') as file:
                json.dump(data, file, indent=2)
            self.config_select()
            close_popup()

        with popup("添加配置"):
            put_input("new_config", label="配置名")
            put_select("copy_from_config", label="从现有配置复制",
                       options=[(x.split(".")[0], x) for x in self.configs])
            put_buttons(["确定", "取消"], onclick=[add_confirm, close_popup])

    def delete_config(self):
        if self.config == "template.json":
            toast("不能删除模板配置", color="error")
            return

        def delete_confirm():
            conf = pin['config']
            self.config = "template.json"
            os.remove(f"config/{conf}")
            self.config_select()
            close_popup()

        with popup("真的要删除吗？"):
            put_buttons(["确定", "取消"], onclick=[delete_confirm, close_popup])

    def set_name(self, name):
        self.data['essential']['name'] = name

    def set_dataset_path(self, path):
        self.data['essential']['dataset_path'] = path

    def set_dataset_type(self, dataset_type):
        self.data['essential']['dataset_type'] = dataset_type

    def set_label_type(self, label_type):
        self.data['essential']['label_type'] = label_type

    def set_use_empty_background(self, use_empty_background):
        self.data['essential']['use_empty_background'] = use_empty_background

    def set_init_seed(self, init_seed):
        self.data['essential']['init_seed'] = init_seed

    def set_category_enabled(self, category, enabled):
        self.data['categories'][category]['enabled'] = len(enabled) > 0

    def set_category_path(self, category, path):
        self.data['categories'][category]['path'] = path

    def set_category_cls(self, category, cls):
        self.data['categories'][category]['cls'] = cls

    def set_category_min_max(self, category, min_num=None, max_num=None):
        d = self.data['categories'][category]
        if min_num is not None and min_num >= 0:
            d['min_num'] = min_num
        if max_num is not None and max_num >= 0:
            d['max_num'] = max_num

    def set_category_rotate(self, category, rotate):
        self.data['categories'][category]['rotate'] = len(rotate) > 0

    def set_category_checked(self, category, checked, unique_prefix, func):
        options_all = func()
        if not set(checked).issubset(set(options_all)):
            checked = []
        self.data['categories'][category]['checked'] = checked
        pin_update(unique_prefix + "checked", value=checked)

    def add_category(self):
        def add_confirm():
            new_category = pin['new_category']
            if new_category is None:
                toast("类别名不能为空", color="error")
                return
            self.data['categories'][new_category] = {
                "enabled": False,
                "cls": 0,
                "rotate": False,
                "path": "",
                "min_num": 0,
                "max_num": 0,
                "checked": []
            }
            self.categories()
            self.essential()
            close_popup()

        with popup("添加类别"):
            put_input("new_category", label="类别名")
            put_buttons(["确定", "取消"], onclick=[add_confirm, close_popup])

    def delete_category(self, category):
        del self.data['categories'][category]
        self.categories()
        self.essential()


def main():
    gui = JsonEditorGUI()
    gui.run()


if __name__ == '__main__':
    start_server(main, debug=True, port=8081, auto_open_webbrowser=True, cdn=False)
