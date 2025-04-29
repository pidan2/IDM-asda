import os
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
from PIL import Image, ImageTk

# === 这里替换为你的模块路径 ===
from feature_extral_comp import FeatureExtAndComp
from config import Config
from store_manager import get_store_info

# 模拟评价数据存储
reviews = {}

# ================= 登录注册界面 =================
import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk


class LoginRegisterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("线下门店服饰推荐系统")
        self.root.geometry("400x300")

        # 加载背景图片
        try:
            self.bg_image = Image.open(
                "D:/graduate project/image_retrieval_with_gui-master (2)/image_retrieval_with_gui-master/test/background/0575232b15ce40f4e576411ae220feb.jpg")
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            messagebox.showerror("错误", "未找到背景图片 ")
            self.root.destroy()
            return

        style = ttk.Style()
        style.theme_use('default')
        # 设置标签背景透明
        style.configure('TLabel', background="transparent", font=('Arial', 15))
        # 设置输入框样式，使其透明
        style.configure('TEntry', fieldbackground="transparent", font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12))

        # 添加文字介绍
        self.introduction_label = ttk.Label(
            root, text="线下门店服饰推荐系统", font=('Arial', 16, 'bold'), foreground='white')
        self.introduction_label.place(relx=0.5, rely=0.1, anchor="center")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.username_placeholder = "请输入账号"
        self.password_placeholder = "请输入密码"

        self.username_entry = ttk.Entry(root, textvariable=self.username_var)
        self.username_entry.insert(0, self.username_placeholder)
        self.username_entry.bind("<FocusIn>",
                                 lambda args: self.clear_placeholder(self.username_entry, self.username_placeholder))
        self.username_entry.bind("<FocusOut>",
                                 lambda args: self.restore_placeholder(self.username_entry, self.username_placeholder))
        self.username_entry.place(relx=0.5, rely=0.35, anchor="center")

        ttk.Label(root, text="用户名:").place(relx=0.5, rely=0.3, anchor="center")

        self.password_entry = ttk.Entry(root, textvariable=self.password_var)
        self.password_entry.insert(0, self.password_placeholder)
        self.password_entry.bind("<FocusIn>", lambda args: self.clear_placeholder_password(self.password_entry,
                                                                                           self.password_placeholder))
        self.password_entry.bind("<FocusOut>", lambda args: self.restore_placeholder_password(self.password_entry,
                                                                                              self.password_placeholder))
        self.password_entry.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(root, text="密码:").place(relx=0.5, rely=0.45, anchor="center")

        # 设置登录按钮颜色为蓝色
        self.login_button = ttk.Button(
            root, text="登录", command=self.login, style="Blue.TButton")
        self.login_button.place(relx=0.5, rely=0.65, anchor="center")

        # 设置注册按钮颜色为蓝色
        self.register_button = ttk.Button(
            root, text="注册", command=self.register, style="Blue.TButton")
        self.register_button.place(relx=0.5, rely=0.8, anchor="center")

        # 定义蓝色按钮样式
        style.configure("Blue.TButton", foreground="white", background="#0078d7")

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)

    def clear_placeholder_password(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(show="*")

    def restore_placeholder_password(self, entry, placeholder):
        if not entry.get():
            entry.config(show="")
            entry.insert(0, placeholder)

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if username == self.username_placeholder:
            username = ""
        if password == self.password_placeholder:
            password = ""

        if not os.path.exists("users.txt"):
            messagebox.showerror("错误", "尚未注册任何用户")
            return

        with open("users.txt", "r") as f:
            for line in f:
                saved_user, saved_pass = line.strip().split(":")
                if username == saved_user and password == saved_pass:
                    messagebox.showinfo("成功", "登录成功")
                    self.root.withdraw()
                    main_window = tk.Toplevel(self.root)
                    RetrieverGUI(main_window)
                    main_window.protocol("WM_DELETE_WINDOW", lambda: self.quit_app(main_window))
                    main_window.mainloop()
                    return

        messagebox.showerror("失败", "用户名或密码错误")

    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if username == self.username_placeholder:
            username = ""
        if password == self.password_placeholder:
            password = ""

        if not username or not password:
            messagebox.showwarning("警告", "用户名和密码不能为空")
            return

        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                for line in f:
                    if username == line.strip().split(":")[0]:
                        messagebox.showerror("错误", "用户已存在")
                        return

        with open("users.txt", "a") as f:
            f.write(f"{username}:{password}\n")
        messagebox.showinfo("注册成功", "请点击登录")

    def quit_app(self, main_window):
        main_window.destroy()
        self.root.destroy()


# ================= 图像检索主界面 =================
class RetrieverGUI:
    def __init__(self, window):
        self.retriever = FeatureExtAndComp(
            Config.arch_name,
            Config.class_nums,
            Config.input_size,
            Config.batch_size,
            Config.feature_layers,
            Config.feature_index_in_module,
            Config.pretrained
        )

        self.parent = window
        self.parent.title("线下门店服饰推荐系统")

        self.frame = Frame(self.parent)
        self.frame.grid(row=0, column=0, sticky=W)

        # 目标图片选择区域
        self.contrast_label = Label(self.frame, text="目标图片:")
        self.contrast_label.grid(row=0, column=0, sticky=W)

        self.contrast_entry = Entry(self.frame)
        self.contrast_entry.grid(row=0, column=1, sticky=W)

        self.contrast_btn = Button(self.frame, text="加载", command=self.choose_contrast_file)
        self.contrast_btn.grid(row=0, column=2, sticky=W)

        self.contrast_panel = Canvas(self.frame)
        self.contrast_panel.grid(row=1, column=0, rowspan=2, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)

        # 搜索按钮
        self.btn = Button(self.frame, text="搜索", command=self.get_retriever_top)
        self.btn.grid(row=1, column=3, sticky=W + E)

        # 搜索目录区域
        self.retrieved_label = Label(self.frame, text="搜索目录:")
        self.retrieved_label.grid(row=0, column=4, sticky=W)

        self.retrieved_entry = Entry(self.frame)
        self.retrieved_entry.grid(row=0, column=5, sticky=W)

        self.retrieved_btn = Button(self.frame, text="加载", command=self.choose_retrieved_dir)
        self.retrieved_btn.grid(row=0, column=6, sticky=W + E)

        self.result_panel1 = Frame(self.frame)
        self.result_panel1.grid(row=1, column=4, rowspan=2, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)

    def choose_retrieved_dir(self):
        self.selectDirName = tkinter.filedialog.askdirectory(title='选择目录')
        if not self.selectDirName or not os.path.exists(self.selectDirName):
            tkinter.messagebox.showerror("错误！", "未选择或目录不存在！")
            return
        self.retrieved_entry.delete(0, END)
        self.retrieved_entry.insert(0, os.path.basename(self.selectDirName))

    def choose_contrast_file(self):
        self.selectFileName = tkinter.filedialog.askopenfilename(
            title='选择文件',
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png")]
        )
        if not self.selectFileName or not os.path.exists(self.selectFileName):
            tkinter.messagebox.showerror("错误！", "未选择或文件不存在！")
            return

        self.contrast_entry.delete(0, END)
        self.contrast_entry.insert(0, os.path.basename(self.selectFileName))

        display_width = 256
        display_height = 256
        self.img_png = Image.open(self.selectFileName)
        self.img_png.thumbnail((display_width, display_height), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(self.img_png)

        self.contrast_panel.config(width=self.tkimg.width(), height=self.tkimg.height())
        self.contrast_panel.create_image(0, 0, image=self.tkimg, anchor=NW)

    def get_retriever_top(self):
        try:
            topN = 8
            result = self.retriever.get_topN(topN, self.selectFileName, self.selectDirName)
            if not result:
                tkinter.messagebox.showinfo("结果", "未找到结果！")
                return

            for widget in self.result_panel1.winfo_children():
                widget.destroy()

            display_width = 256
            display_height = 256
            for i, image_name in enumerate(result):
                # 修正文件名
                if '.' not in image_name:
                    # 假设图片格式为 jpg，可根据实际情况修改
                    image_name = image_name.rsplit('jpg', 1)[0] + '.jpg'

                found = False
                for root, dirs, files in os.walk(self.selectDirName):
                    if image_name in files:
                        result_image_path = os.path.join(root, image_name)
                        found = True
                        break
                if not found:
                    tkinter.messagebox.showerror("错误！", f"图片 {image_name} 不存在")
                    continue

                try:
                    img = Image.open(result_image_path)
                    img.thumbnail((display_width, display_height), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)

                    # 创建一个框架来包含图片和店铺信息
                    panel_frame = Frame(self.result_panel1)
                    panel_frame.grid(row=i // 4, column=i % 4)

                    panel = Label(panel_frame, image=tk_img)
                    panel.image = tk_img
                    panel.pack()

                    # 获取店铺信息


                    # 添加按钮框架，用于布局四个按钮
                    button_frame = tkinter.Frame(panel_frame)
                    button_frame.pack()

                    # 定义按钮颜色列表
                    button_colors = ["#FF0000", "#00FF00", "#87CEEB", "#FFFF00"]

                    # 添加查看评价按钮
                    review_button = tkinter.Button(button_frame, text="查看评价",
                                                   command=lambda path=result_image_path: self.show_review_page(path),
                                                   bg=button_colors[0])
                    review_button.grid(row=0, column=0, padx=5, pady=5)

                    # 添加商品介绍按钮
                    product_button = tkinter.Button(button_frame, text="商品介绍",
                                                    command=lambda path=result_image_path: self.show_product_info(path),
                                                    bg=button_colors[1])
                    product_button.grid(row=0, column=1, padx=5, pady=5)

                    # 添加地址详情按钮
                    address_button = tkinter.Button(button_frame, text="地址详情",
                                                    command=lambda path=result_image_path: self.show_address_info(path),
                                                    bg=button_colors[2])
                    address_button.grid(row=1, column=0, padx=5, pady=5)

                    # 添加点击下单按钮
                    order_button = tkinter.Button(button_frame, text="点击下单",
                                                  command=lambda path=result_image_path: self.show_order_page(path),
                                                  bg=button_colors[3])
                    order_button.grid(row=1, column=1, padx=5, pady=5)

                except Exception as e:
                    tkinter.messagebox.showerror("错误！", f"加载图片 {image_name} 时出错: {str(e)}")
                    print(f"错误详情：{e}")

        except Exception as e:
            tkinter.messagebox.showerror("错误！", f"发生错误: {str(e)}")
            print(f"错误详情：{e}")

    def show_review_page(self, image_path):
        review_window = tk.Toplevel(self.parent)
        review_window.title(f"图片 {os.path.basename(image_path)} 的评价")

        # 显示评价内容
        if image_path in reviews:
            review_text = "\n".join(reviews[image_path])
        else:
            review_text = "暂无评价"
        review_label = Label(review_window, text=review_text)
        review_label.pack()

        # 添加评价输入框和提交按钮
        review_entry = Entry(review_window)
        review_entry.pack()
        submit_button = Button(review_window, text="提交评价",
                               command=lambda: self.submit_review(image_path, review_entry.get(), review_window))
        submit_button.pack()

        # 添加返回按钮
        back_button = Button(review_window, text="返回检索页面", command=review_window.destroy)
        back_button.pack()

    def submit_review(self, image_path, review, review_window):
        if review:
            if image_path not in reviews:
                reviews[image_path] = []
            reviews[image_path].append(review)
            tkinter.messagebox.showinfo("提示", "评价提交成功！")
            review_window.destroy()
            self.show_review_page(image_path)

    def show_product_info(self, image_path):
        product_window = tk.Toplevel(self.parent)
        product_window.title(f"图片 {os.path.basename(image_path)} 的商品介绍")

        # 读取商品介绍.txt文件内容
        product_info_path = os.path.join(os.path.dirname(image_path), "商品介绍.txt")
        try:
            with open(product_info_path, "r", encoding="utf-8") as f:
                product_text = f.read()
            product_label = Label(product_window, text=product_text, justify=LEFT)
            product_label.pack()
        except FileNotFoundError:
            product_text = "暂无商品介绍"
            product_label = Label(product_window, text=product_text, justify=LEFT)
            product_label.pack()

        # 添加返回按钮
        back_button = Button(product_window, text="返回检索页面", command=product_window.destroy)
        back_button.pack()

    def show_address_info(self, image_path):
        address_window = tk.Toplevel(self.parent)
        address_window.title(f"图片 {os.path.basename(image_path)} 的地址详情")

        # 读取地址详情.txt文件内容
        address_info_path = os.path.join(os.path.dirname(image_path), "地址详情.txt")
        try:
            with open(address_info_path, "r", encoding="utf-8") as f:
                address_text = f.read()
            address_label = Label(address_window, text=address_text, justify=LEFT)
            address_label.pack()
        except FileNotFoundError:
            address_text = "暂无地址详情"
            address_label = Label(address_window, text=address_text, justify=LEFT)
            address_label.pack()

        # 添加返回按钮
        back_button = Button(address_window, text="返回检索页面", command=address_window.destroy)
        back_button.pack()

    def show_order_page(self, image_path):
        order_window = tk.Toplevel(self.parent)
        order_window.title(f"图片 {os.path.basename(image_path)} 下单页面")

        # 使用ttk.Style设置整体样式
        style = ttk.Style()
        style.theme_use('clam')  # 选择一种主题，可根据喜好更换
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TEntry', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12), padding=5)

        # 创建主框架，使用网格布局
        main_frame = ttk.Frame(order_window)
        main_frame.pack(padx=20, pady=20)

        # 快递信息输入框部分
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, columnspan=2, pady=10)

        name_label = ttk.Label(info_frame, text="姓名:")
        name_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        name_entry = ttk.Entry(info_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        phone_label = ttk.Label(info_frame, text="电话:")
        phone_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        phone_entry = ttk.Entry(info_frame)
        phone_entry.grid(row=1, column=1, padx=5, pady=5)

        address_label = ttk.Label(info_frame, text="地址:")
        address_label.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        address_entry = ttk.Entry(info_frame)
        address_entry.grid(row=2, column=1, padx=5, pady=5)

        # 颜色选择按钮部分
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=1, column=0, pady=10)

        color_black_button = ttk.Button(color_frame, text="黑色", command=lambda: self.select_color("黑色"))
        color_black_button.grid(row=0, column=0, padx=5, pady=5)
        color_white_button = ttk.Button(color_frame, text="白色", command=lambda: self.select_color("白色"))
        color_white_button.grid(row=0, column=1, padx=5, pady=5)

        # 尺码选择按钮部分
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=1, column=1, pady=10)

        size_s_button = ttk.Button(size_frame, text="S", command=lambda: self.select_size("S"))
        size_s_button.grid(row=0, column=0, padx=5, pady=5)
        size_m_button = ttk.Button(size_frame, text="M", command=lambda: self.select_size("M"))
        size_m_button.grid(row=0, column=1, padx=5, pady=5)
        size_l_button = ttk.Button(size_frame, text="L", command=lambda: self.select_size("L"))
        size_l_button.grid(row=1, column=0, padx=5, pady=5)
        size_xl_button = ttk.Button(size_frame, text="XL", command=lambda: self.select_size("XL"))
        size_xl_button.grid(row=1, column=1, padx=5, pady=5)

        # 提交订单按钮
        submit_order_button = ttk.Button(main_frame, text="提交订单",
                                         command=lambda: self.submit_order(image_path, name_entry.get(),
                                                                           phone_entry.get(),
                                                                           address_entry.get()))
        submit_order_button.grid(row=2, column=0, columnspan=2, pady=10)

        # 返回按钮
        back_button = ttk.Button(main_frame, text="返回检索页面", command=order_window.destroy)
        back_button.grid(row=3, column=0, columnspan=2, pady=10)

    def select_color(self, color):
        print(f"选择的颜色是: {color}")

    def select_size(self, size):
        print(f"选择的尺码是: {size}")

    def submit_order(self, image_path, name, phone, address):
        if name and phone and address:
            tkinter.messagebox.showinfo("提示", "订单提交成功！")
        else:
            tkinter.messagebox.showerror("错误", "请填写完整的快递信息！")


# 启动登录界面
if __name__ == '__main__':
    root = Tk()
    LoginRegisterGUI(root)
    root.mainloop()