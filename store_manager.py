import os


def get_store_info(image_path):
    """获取店铺信息"""
    folder = os.path.dirname(image_path)
    info_path = os.path.join(folder, "info.txt")

    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            return "店铺信息读取失败"
    return "暂无店铺信息"