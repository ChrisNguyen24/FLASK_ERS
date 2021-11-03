import math
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
class Collaborate_Filter:
    def __init__(self, user, S): # hàm khởi tạo
    def initialize(self): # gán data
    def pearson_correlation(self, user1, user2): # tương quan person
    def user_average_rating(self, user_data): # trung bình đánh giá
    def common_items(self, user1_data, user2_data): # get các item chung của
    2 user
    def k_nearest_neighbors(self, user, item, k): # get k láng giềng gần
    nhất
    def listPredict(self, user_id): #get các item được dự đoán
    def predict(self ,user, item, k_nearest_neighbors): # tính toán các
    rating còn thiếu
    def load_data(self, ratings_file): # xử lý data đầu vào thành các biến
    def display(self, list_predicts): # hiển thị kết quả
    def main(self): # Hàm main
if __name__ == '__main__':
    cf = Collaborate_Filter(user, S)
    cf.initialize()
    cf.main()


# Giới thiệu về hệ thống tư vấn 
# Các kỹ thuật sử dụng và các cách tiếp cận
#Hướng tiếp cận của đồ án.