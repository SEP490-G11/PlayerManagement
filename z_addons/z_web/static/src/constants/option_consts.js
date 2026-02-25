/** @odoo-module **/


// Labels
export const labelOptions = {
  filter: "Bộ lọc",
  doctor: "Bác sĩ",
  technician: "Kỹ thuật viên",
  group: "Nhóm",
  from: "Từ",
  gender: "Giới tính",
  to: "Đến",
  sort: "Sắp xếp",
  state: "Trạng thái",
  doctorTab: "Lịch bác sĩ",
  optomTab: "Lịch optom",
  doctorTableHeader: "Lịch làm việc bác sĩ",
  optomTableHeader: "Lịch làm việc optom",
};

export const specialistRoleOptions = {
  doctor: "Bác sĩ",
  optom: "Optom",
};

export const genderOptions = [
  {
    value: "male",
    label: "Nam",
  },
  {
    value: "female",
    label: "Nữ",
  },
];

export const contactOptions = [
  {
    value: "1",
    label: "Fanpage",
  },
  {
    value: "2",
    label: "Hotline",
  },
  {
    value: "3",
    label: "Zalo OA",
  },
  {
    value: "4",
    label: "Website",
  },
  {
    value: "5",
    label: "Team",
  },
  {
    value: "6",
    label: "Campain",
  },
  {
    value: "8",
    label: "Google Ads",
  },
  {
    value: "9",
    label: "Tự đến",
  },
  {
    value: "10",
    label: "Khám sàng lọc",
  },
  {
    value: "11",
    label: "Khác",
  },
]

export const approachChannelOptions =  [
  { value: "1", label: 'Group FB' },
  { value: "2", label: 'FB (Fanpage)' },
  { value: "3", label: 'Google' },
  { value: "4", label: 'Website' },
  { value: "5", label: 'Tiktok' },
  { value: "6", label: 'Youtube' },
  { value: "7", label: 'Người giới thiệu' },
  { value: "8", label: 'Trang chuyên gia' },
  { value: "9", label: 'Vãng lai' }
];

// Sort
export const nameSortOptions = [
  {
    value: 1,
    label: "Tăng dần theo Alphabet",
  },
  {
    value: 2,
    label: "Giảm dần theo Alphabet",
  },
];

export const createDateSortOptions = [
  {
    value: 3,
    label: "Ngày tạo mới nhất",
  },
  {
    value: 4,
    label: "Ngày tạo cũ nhất",
  },
];

export const dobSortOptions = [
  {
    value: 5,
    label: "Ngày sinh gần nhất",
  },
  {
    value: 6,
    label: "Ngày sinh xa nhất",
  },
];

export const appointmentSortOptions = [
  {
    value: 1,
    label: "Theo thời gian khám mới nhất",
  },
  {
    value: 2,
    label: "Theo thời gian khám cũ nhất",
  },
];

export const defaultSortByName = 1;

export const defaultSortByCreateDate = 3;

export const defaultAppointmentSort = 1;

export const defaultAppointmentSortObstetric = 2;

// Appointment
export const appointmentStatusOptions = [
  {
    value: "1",
    label: "Chưa đến",
  },
  {
    value: "2",
    label: "Chờ khám",
  },
  {
    value: "3",
    label: "Đang khám",
  },
  {
    value: "4",
    label: "Tư vấn",
  },
  {
    value: "5",
    label: "Kết thúc",
  },
  {
    value: "6",
    label: "CBSKL",
  },
  {
    value: "7",
    label: "Cyclogyl",
  },
  {
    value: "8",
    label: "CLS",
  },
  {
    value: "9",
    label: "Hết hạn",
  },
];

export const appointmentTypeOptions = [
  {
    value: "1",
    label: "Khám mới",
  },
  {
    value: "2",
    label: "Tái khám",
  },
];

// Examination
export const visitStatus = ["3", "4", "5", "6", "7", "8", "9"];

export const measurementTypeOptions = [
  {
    value: "SC",
    label: "SC",
  },
  {
    value: "CC",
    label: "CC",
  },
];

export const refractiveMedicineOptions = [
  {
    value: "1",
    label: "Cyclogyl 1%",
  },
  {
    value: "2",
    label: "Atropin 0.5%",
  },
];

export const timeUntilReexaminationOptions = [
  {
    value: "1",
    label: "Không",
  },
  {
    value: "2",
    label: "1 ngày",
  },
  {
    value: "3",
    label: "2 ngày",
  },
  {
    value: "4",
    label: "3 ngày",
  },
  {
    value: "5",
    label: "4 ngày",
  },
  {
    value: "6",
    label: "5 ngày",
  },
  {
    value: "7",
    label: "1 tuần",
  },
  {
    value: "8",
    label: "2 tuần",
  },
  {
    value: "9",
    label: "3 tuần",
  },
  {
    value: "10",
    label: "1 tháng",
  },
  {
    value: "11",
    label: "2 tháng",
  },
  {
    value: "12",
    label: "3 tháng",
  },
  {
    value: "13",
    label: "6 tháng",
  },
  {
    value: "14",
    label: "1 năm",
  },
  {
    value: "15",
    label: "Khác",
  },
];

export const clsOptions = [
  {
    value: "1",
    label: "Bóc giả mạc",
  },
  {
    value: "2",
    label: "Chích chắp/lẹo",
  },
  {
    value: "3",
    label: "Chụp bản đồ giác mạc",
  },
  {
    value: "4",
    label: "Đánh rửa bờ mi",
  },
  {
    value: "5",
    label: "Đánh rửa kính tiếp xúc chuyên sâu",
  },
  {
    value: "6",
    label: "Đo nhãn áp",
  },
  {
    value: "7",
    label: "Giảm 10% tiền khám",
  },
  {
    value: "8",
    label: "Khám khiếm thị",
  },
  {
    value: "9",
    label: "Khám kính tiếp xúc",
  },
  {
    value: "10",
    label: "Khám KX liệt điều tiết",
  },
  {
    value: "11",
    label: "Khám mắt ban đầu",
  },
  {
    value: "12",
    label: "Khám thị giác 2 mắt",
  },
  {
    value: "13",
    label: "Lấy sạn vôi, dị vật",
  },
  {
    value: "14",
    label: "Miễn phí khám",
  },
  {
    value: "15",
    label: "Sinh Trắc Học",
  },
  {
    value: "16",
    label: "Tái khám gói dịch vụ",
  },
  {
    value: "17",
    label: "Tái khám Ortho-K",
  },
  {
    value: "18",
    label: "Thay băng cắt chỉ",
  },
  {
    value: "19",
    label: "Thông tắc lệ đạo",
  },
  {
    value: "20",
    label: "Thử thông số kính Ortho-K",
  },
  {
    value: "21",
    label: "Thử thông số kính tiếp xúc mềm",
  },
];

export const vendorStatusOptions = [
  { id: "1", value: "Đang hoạt động" },
  { id: "2", value: "Tạm dừng" },
];
