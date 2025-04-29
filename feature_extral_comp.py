# 导入必要的库
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import random
import os
import torchvision
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm

def default_loader(path):
    try:
        return Image.open(path).convert('RGB')
    except Exception as e:
        print(f"Error opening image {path}: {e}")
        return None

class MyDataset(Dataset):
    def __init__(self, images_path, transform=None, loader=default_loader):
        self.images_path = []
        for root, dirs, files in os.walk(images_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.images_path.append(os.path.join(root, file))
        self.transform = transform
        self.loader = loader

    def __getitem__(self, index):
        path = self.images_path[index]
        img = self.loader(path)
        if self.transform is not None:
            img = self.transform(img)
        return img, path

    def __len__(self):
        return len(self.images_path)

class FeatureExtAndComp(object):
    def __init__(self, arch_name: str,
                 num_classes: int,
                 input_size: int,
                 batch_size: int,
                 feature_layers: list,  # 传入多个特征层
                 feature_index_in_module: int,  # 添加这个参数
                 pretrained: bool = True,
                 cuda: bool = True):
        self.arch_name = arch_name
        self.num_classes = num_classes
        self.input_size = input_size
        self.batch_size = batch_size
        self.feature_layers = feature_layers
        self.feature_index_in_module = feature_index_in_module
        self.pretrained = pretrained
        self.cuda = cuda
        self.model = torchvision.models.__dict__[arch_name](pretrained=pretrained)
        if num_classes > 0:
            num_ftrs = self.model.fc.in_features
            self.model.fc = torch.nn.Linear(num_ftrs, num_classes)
        if cuda:
            self.model = self.model.cuda()
        self.model.eval()
        self.feature_maps = {}
        for layer in feature_layers:
            getattr(self.model, layer).register_forward_hook(self.hook_feature(layer))

    def hook_feature(self, layer_name):
        def hook(module, input, output):
            self.feature_maps[layer_name] = output
        return hook

    def get_data_loader(self, images_folder_path):
        transform = transforms.Compose([
            transforms.Resize((self.input_size, self.input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        dataset = MyDataset(images_folder_path, transform=transform)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        return data_loader

    def extract_batch_features(self, images_folder_path):
        data_loader = self.get_data_loader(images_folder_path)
        all_features = []
        all_filenames = []
        with torch.no_grad():
            for images, paths in tqdm(data_loader):
                if self.cuda:
                    images = images.cuda()
                self.model(images)
                features = self.feature_maps[self.feature_layers[self.feature_index_in_module]]
                features = features.view(features.size(0), -1)
                all_features.extend(features.cpu().numpy())
                all_filenames.extend(paths)
        return all_features, all_filenames

    def extract_single_features(self, test_images):
        transform = transforms.Compose([
            transforms.Resize((self.input_size, self.input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        img = Image.open(test_images).convert('RGB')
        img = transform(img).unsqueeze(0)
        if self.cuda:
            img = img.cuda()
        with torch.no_grad():
            self.model(img)
            features = self.feature_maps[self.feature_layers[self.feature_index_in_module]]
            features = features.view(features.size(0), -1)
        return features.cpu().numpy()

    def get_topN(self, topN, single_image, batch_images_path):
        single_feature = self.extract_single_features(single_image)
        batch_features, batch_filenames = self.extract_batch_features(batch_images_path)
        distances = []
        for feature in batch_features:
            distance = np.linalg.norm(single_feature - feature)
            distances.append(distance)
        sorted_indices = np.argsort(distances)[:topN]
        result = [os.path.basename(batch_filenames[i]) for i in sorted_indices]
        return result

    def caculate_distance(self, feature):
        print(f"Feature shape: {feature.shape}")  # 打印特征形状（调试用）