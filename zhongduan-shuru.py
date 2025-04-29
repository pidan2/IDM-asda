#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from PIL import Image
from feature_extral_comp import FeatureExtAndComp
from config import Config

class RetrieverTool:
    def __init__(self):
        self.retriever = FeatureExtAndComp(
            Config.arch_name,
            Config.class_nums,
            Config.input_size,
            Config.batch_size,
            Config.feature_layers,
            Config.feature_index_in_module,
            Config.pretrained
        )
        self.selectDirName = ""
        self.selectFileName = None

    # ...其余方法保持不变...

    def set_contrast_file_path(self, file_path):  # 设置目标图片路径
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的图片路径不存在：{file_path}")
        self.selectFileName = file_path
        print(f"已设置目标图片路径：{file_path}")

    def set_search_directory(self, dir_path):  # 设置检索目录
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"指定的检索目录不存在：{dir_path}")
        self.selectDirName = dir_path
        print(f"已设置检索目录路径：{dir_path}")

    def get_retriever_top(self):  # 获取检索结果
        if not self.selectFileName:
            raise ValueError("未设置目标图片路径，请先调用 set_contrast_file_path 方法。")
        if not self.selectDirName:
            raise ValueError("未设置检索目录路径，请先调用 set_search_directory 方法。")

        try:
            topN = 10  # 检索前10个结果
            result = self.retriever.get_topN(topN, self.selectFileName, self.selectDirName)
            if not result or not isinstance(result, list) or len(result) == 0:
                print("未找到任何结果！")
                return []

            full_paths = [os.path.join(self.selectDirName, image_name) for image_name in result]
            print("检索结果：")
            # for path in full_paths:
            #     #print(path)
            return full_paths

        except Exception as e:
            print(f"检索过程中发生错误：{str(e)}")
            return []

    def get_top_image_paths(self):  # 输出检索结果的完整路径
        try:
            topN = 10  # 设置要返回的图片数量为10
            result = self.get_retriever_top()
            if not result:
                return "未找到结果！"
            result_string = "\n".join(result)  # 用换行符拼接成字符串
            return result_string
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return ""


# 示例调用
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Usage: python retriever_tool.py <image_path> <directory_path>")
        sys.exit(1)

    # 获取命令行参数
    image_path = sys.argv[1]  # 图片路径
    directory_path = sys.argv[2]  # 检索目录路径

    # 初始化工具并设置路径
    retriever = RetrieverTool()
    retriever.set_contrast_file_path(image_path)
    retriever.set_search_directory(directory_path)

    # 获取检索结果
    result = retriever.get_top_image_paths()
    print(result)
