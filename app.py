import json
import os
from functools import partial

from pywebio import *
from pywebio.output import *
from pywebio.pin import *


class JsonEditorGUI:
    add_icon = "\U00002795"
    delete_icon = "\U0000274C"
    save_icon = "\U0001F4BE"
    refresh_icon = "\U0001F504"

    def __init__(self, config="template.json"):
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

    @use_scope("ROOT", clear=True)
    def home(self):
        put_row([
            put_scope("config_select"),
            None,
            put_tabs([
                {"title": "基本设置", "content": put_scope("essential")},
                {"title": "类别设置", "content": put_scope("categories")},
            ])
        ], size="25% 5% 70%")

    @use_scope("config_select", clear=True)
    def config_select(self):
        self.configs = [f for f in os.listdir('config') if f.endswith('.json')]
        options = [(f.split(".")[0], f) for f in self.configs if f.endswith('.json')]
        put_select("config", label="Config", options=options, value=self.config)

        put_buttons([self.save_icon, self.refresh_icon, self.add_icon, self.delete_icon],
                    onclick=[self.save_config, self.config_select, self.add_config, self.delete_config])

        pin_on_change("config", onchange=self.set_config, clear=True)

    @use_scope("essential", clear=True)
    def essential(self):
        data_ess = self.data['essential']
        put_input("name", label="数据集名", value=data_ess['name'])
        put_input("dataset_path", label="数据集路径", value=data_ess['dataset_path'])
        put_select("dataset_type", label="数据集类型", options=[("训练集", "train"),
                                                                ("验证集", "val"),
                                                                ("测试集", "test")], value=data_ess['dataset_type'])
        put_select("label_type", label="标签形式", options=[('掩码', 'mask'), ('YOLO标注框', 'yolo_detect')],
                   value=data_ess['label_type'])

        bg_enabled = "background" in self.data['categories']

        put_select("use_empty_background", label="背景样式",
                   options=[dict(label='纯黑背景', value=True),
                            dict(label='自定义背景' + ("" if bg_enabled else "（需要添加名为\"background\"的类别）"),
                                 value=False, disabled=not bg_enabled)],
                   value=data_ess['use_empty_background'])
        put_input("init_seed", label="初始化种子", type='number', value=data_ess['init_seed'])

        pin_on_change("name", onchange=self.set_name, clear=True)
        pin_on_change("dataset_path", onchange=self.set_dataset_path, clear=True)
        pin_on_change("dataset_type", onchange=self.set_dataset_type, clear=True)
        pin_on_change("label_type", onchange=self.set_label_type, clear=True)
        pin_on_change("use_empty_background", onchange=self.set_use_empty_background, clear=True)
        pin_on_change("init_seed", onchange=self.set_init_seed, clear=True)

    @use_scope("categories", clear=True)
    def categories(self):
        for category in self.data['categories']:
            self.category(category)
        put_button("添加类别", onclick=self.add_category)

    def category(self, category):
        with use_scope(f"categories_{category}", clear=True):
            data_cat = self.data['categories'][category]
            options_all = [f for f in os.listdir(f"{data_cat['path']}")] if data_cat['path'] else []

            def set_ops():
                new_options_all = [f for f in os.listdir(f"{data_cat['path']}")] if data_cat['path'] else []
                nonlocal options_all
                if set(options_all) != set(new_options_all):
                    options_all = new_options_all
                    pin_update(f"{category}_checked", options=options_all)
                return new_options_all

            set_checked = partial(self.set_category_checked, category, func=set_ops)

            put_row([
                put_collapse(category, [
                    put_checkbox(f"{category}_enabled", options=[("启用", "enabled", data_cat['enabled'])]),
                    put_input(f"{category}_path", label="路径", value=data_cat['path']),
                    put_input(f"{category}_cls", label="类别id", type='number', value=data_cat['cls']),
                    put_row([
                        put_input(f"{category}_min_num", label="最小数量", type='number', value=data_cat['min_num']),
                        None,
                        put_input(f"{category}_max_num", label="最大数量", type='number', value=data_cat['max_num']),
                        None
                    ], size="1fr 0.2fr 1fr 5fr"),
                    put_checkbox(f"{category}_rotate", options=[("随机旋转", "rotate", data_cat['rotate'])]),
                    put_row([
                        put_collapse("子类别", content=[
                            put_scrollable(
                                put_checkbox(f"{category}_checked", options=options_all, value=data_cat['checked']),
                                height=(0, 200)),
                            put_buttons(["全选", "全不选"],
                                        onclick=[lambda: set_checked(options_all), lambda: set_checked([])])
                        ], open=True),
                        None,
                        put_button(self.refresh_icon, onclick=lambda: set_checked(data_cat['checked']))
                    ], size="88% 2% 10%")
                ]),
                None,
                put_button(self.delete_icon, onclick=lambda: self.delete_category(category))
            ], size="88% 2% 10%")

            pin_on_change(f"{category}_enabled", onchange=lambda x: self.set_category_enabled(category, x), clear=True)
            pin_on_change(f"{category}_path", onchange=lambda x: self.set_category_path(category, x), clear=True)
            pin_on_change(f"{category}_cls", onchange=lambda x: self.set_category_cls(category, x), clear=True)
            pin_on_change(f"{category}_min_num", onchange=lambda x: self.set_category_min_max(category, min_num=x),
                          clear=True)
            pin_on_change(f"{category}_max_num", onchange=lambda x: self.set_category_min_max(category, max_num=x),
                          clear=True)
            pin_on_change(f"{category}_rotate", onchange=lambda x: self.set_category_rotate(category, x), clear=True)
            pin_on_change(f"{category}_checked", onchange=set_checked, clear=True)

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

    def set_category_checked(self, category, checked, func):
        all = func()
        if not set(checked).issubset(set(all)):
            checked = []
        self.data['categories'][category]['checked'] = checked
        pin_update(f"{category}_checked", value=checked)

    def add_category(self):
        def add_confirm():
            new_category = pin['new_category']
            if new_category is None:
                toast("类别名不能为空", color="error")
                return
            self.data['categories'][new_category] = {
                "enabled": False,
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
    start_server(main, debug=True, port=8080, auto_open_webbrowser=True, cdn=False)
