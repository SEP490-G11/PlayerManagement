# Báo Cáo Kho Đầu Kỳ Cuối Kỳ

## Mô tả
Module này cung cấp tính năng tạo báo cáo kho đầu kỳ cuối kỳ trong Odoo, cho phép theo dõi tình hình tồn kho theo thời gian.

## Tính năng
- **Wizard chọn thời gian**: Cho phép người dùng chọn khoảng thời gian báo cáo
- **Tính toán tự động**: Tự động tính toán tồn đầu kỳ, nhập, xuất và tồn cuối kỳ
- **Báo cáo PDF**: Xuất báo cáo dưới dạng PDF với giao diện đẹp
- **Tổng hợp dữ liệu**: Hiển thị tổng cộng cho từng cột

## Cách sử dụng

### 1. Truy cập báo cáo
- Vào menu **Kho > Báo cáo > Báo Cáo Kho Đầu Kỳ Cuối Kỳ**

### 2. Chọn thời gian
- **Từ ngày**: Ngày bắt đầu kỳ báo cáo
- **Đến ngày**: Ngày kết thúc kỳ báo cáo

### 3. Tạo báo cáo
- Nhấn nút **"In Báo Cáo"** để tạo báo cáo PDF

## Cách tính toán

### Tồn đầu kỳ
- Tính dựa trên tất cả các stock moves hoàn thành trước ngày bắt đầu kỳ
- Công thức: Tổng nhập vào kho nội bộ - Tổng xuất từ kho nội bộ

### Nhập trong kỳ
- Tổng số lượng từ các stock moves nhập vào kho nội bộ trong kỳ báo cáo
- Chỉ tính các moves có trạng thái "done"

### Xuất trong kỳ
- Tổng số lượng từ các stock moves xuất từ kho nội bộ trong kỳ báo cáo
- Chỉ tính các moves có trạng thái "done"

### Tồn cuối kỳ
- Công thức: Tồn đầu kỳ + Nhập - Xuất

## Cấu trúc báo cáo

### Bảng dữ liệu
| STT | Tên sản phẩm | Mã sản phẩm | Đơn vị | Tồn đầu kỳ | Nhập | Xuất | Tồn cuối kỳ |
|-----|-------------|-------------|--------|-----------|------|------|-------------|
| 1   | Sản phẩm A  | SP001       | Cái    | 100       | 50   | 30   | 120         |

### Thông tin báo cáo
- Thời gian báo cáo
- Ngày in và người in
- Ghi chú giải thích các cột
- Chữ ký người lập, kiểm tra, duyệt

## Lưu ý
- Báo cáo chỉ tính các sản phẩm có hoạt động nhập/xuất
- Dữ liệu dựa trên stock moves có trạng thái "done"
- Chỉ tính các kho có usage = "internal"
- Đơn vị tính theo UoM của sản phẩm

## Cài đặt
1. Cài đặt module `z_stock`
2. Cấp quyền cho nhóm `stock.group_stock_user`
3. Truy cập menu báo cáo trong Kho > Báo cáo
