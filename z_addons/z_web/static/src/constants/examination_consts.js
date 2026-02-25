/** @odoo-module **/

export const defaultComprehensiveExamination = {
  appointment_id: null, //id lịch hẹn, required
  reason: "", //Lý do khám, required
  optometrist: null, //id người đo
  examiner: null, //id người khám
  examination_at: null, //ngày khám, format: yyyy-mm-dd
  reexamination_at: null, //ngày tái khám, format: yyyy-mm-dd
  time_until_reexamination: "", //số ngày đến ngày tái khám, được define ở mục Note
  tracking_element: "", //yếu tố theo dõi
  note: "", //lưu ý

  //Sinh trắc học mắt phải
  right_eye_eyeball_axis_length: "", //chiều dài trục nhãn cầu
  right_eye_gm_thickness: "", //chiều dày gm trung tâm
  right_eye_pupil_size: "", //kích thước đồng tử
  right_eye_acd: "", //acd
  right_eye_steep_or_flat_k: "", //steep k/flat

  //Sinh trắc học mắt trái
  left_eye_eyeball_axis_length: "", //chiều dài trục nhãn cầu
  left_eye_gm_thickness: "", //chiều dày gm trung tâm
  left_eye_pupil_size: "", //kích thước đồng tử
  left_eye_acd: "", //acd
  left_eye_steep_or_flat_k: "", //steep k/flat

  //Thị lực mắt phải
  right_eye_without_glasses: "", //không kính
  right_eye_old_glasses: "", //kính cũ (ô thứ nhất)
  right_eye_old_glasses_unit: "", //kính cũ đơn vị (ô thứ 2)

  //Thị lực mắt trái
  left_eye_without_glasses: "", //không kính
  left_eye_old_glasses: "", //kính cũ (ô thứ nhất)
  left_eye_old_glasses_unit: "", //kính cũ đơn vị (ô thứ 2)

  //Thị lực hai mắt
  eyes_without_glasses: "", //không kính
  eyes_old_glasses: "", //kính cũ (ô thứ nhất)
  eyes_old_glasses_unit: "", //kính cũ đơn vị (ô thứ 2)

  //Thị lực gần
  measurement_type: "", //gửi lên 1 trong 2 giá trị define ở mục Note
  oculus_dexter: "", //mắt phải
  oculus_sinister: "", //mắt trái

  //Hệ phân tụ và vận nhãn
  ct: "",
  npc: "",
  eom: "",

  //Tật khúc xạ - trước liệt mắt phải
  right_eye_objective_anterior_refraction: "", //khách quan - ô đầu
  right_eye_objective_anterior_refraction_unit: "", //khách quan - ô sau
  right_eye_subjective_anterior_refraction: "", //chủ quan - ô đầu
  right_eye_subjective_anterior_refraction_unit: "", //chủ quan - ô sau

  //Tật khúc xạ - trước liệt mắt phải
  left_eye_objective_anterior_refraction: "", //khách quan - ô đầu
  left_eye_objective_anterior_refraction_unit: "", //khách quan - ô sau
  left_eye_subjective_anterior_refraction: "", //chủ quan - ô đầu
  left_eye_subjective_anterior_refraction_unit: "", //chủ quan - ô sau

  add: "",

  //Tật khúc xạ sau liệt
  refractive_medicines: [], //thuốc, gửi lên một list giá trị define ở mục Note
  //Mắt phải
  right_eye_objective_paralytic_refraction: "", //khách quan - ô đầu
  right_eye_objective_paralytic_refraction_unit: "", //khách quan - ô sau
  right_eye_subjective_paralytic_refraction: "", //chủ quan - ô đầu
  right_eye_subjective_paralytic_refraction_unit: "", //chủ quan - ô sau
  //Mắt trái
  left_eye_objective_paralytic_refraction: "", //khách quan - ô đầu
  left_eye_objective_paralytic_refraction_unit: "", //khách quan - ô sau
  left_eye_subjective_paralytic_refraction: "", //chủ quan - ô đầu
  left_eye_subjective_paralytic_refraction_unit: "", //chủ quan - ô sau

  eye_health: "", //sức khoẻ mắt
  cls: [], //chỉ định cls, gửi lên một list giá trị cách nhau bằng dấu phẩy, define ở mục Note
  diagnose: "", //chẩn đoán
  solution: "", //xử lý và tư vấn

  // Đơn kính
  right_eye_glasses_prescription: "", //mắt phải
  left_eye_glasses_prescription: "", //mắt trái
  add_glasses_prescription: "", //add

  //Đơn thuốc
  prescription: [],
};

export const defaultContactExamination = {
  appointment_id: null, //id lịch hẹn, required
  optometrist: null, //id người đo
  examiner: null, //id người khám
  examination_at: null, //Ngày khám,  format: yyyy-mm-dd
  reexamination_at: null, //Ngày tái khám,  format: yyyy-mm-dd
  time_until_reexamination: "", //Số ngày đến ngày tái khám
  reason: "", //Lý do khám, required
  note: "", // Lưu ý
  cls: [], // Chỉ định CLS
  result: "", // Kết quả khám
  solution: "", // Phương án xử lý
  biomicroscopy: "", // Sinh hiển vi
  test_glasses: [], //kính thử
  // Đơn thuốc
  prescription: [],
  // Đơn kính
  right_eye_glasses_brand: "", // Hãng kính
  right_eye_bc: "", // BC
  right_eye_p: "", // P
  right_eye_dia: "", // DIA
  right_eye_vision: "", // Thị lực
  left_eye_glasses_brand: "", // Hãng kính
  left_eye_bc: "", // BC
  left_eye_p: "", // P
  left_eye_dia: "", // DIA
  left_eye_vision: "", // Thị lực
  // Khúc xạ chủ quan
  right_eye_subjective_refraction: "", // Mắt phải
  left_eye_subjective_refraction: "", // Mắt trái
  // Độ cong
  right_eye_flat_k_first: "", //Flat k
  right_eye_flat_k_second: "", // Flat k
  right_eye_flat_k_third: "", // Flat k
  right_eye_steep_k_first: "", // Steep k
  right_eye_steep_k_second: "", // Steep k
  right_eye_steep_k_third: "", // Steep k
  left_eye_flat_k_first: "", //Flat k
  left_eye_flat_k_second: "", //Flat k
  left_eye_flat_k_third: "", //Flat k
  left_eye_steep_k_first: "", // Steep k
  left_eye_steep_k_second: "", // Steep k
  left_eye_steep_k_third: "", // Steep k
  // Đường kính giác mạc
  right_eye_corneal_diameter: "", // Mắt phải
  left_eye_corneal_diameter: "", // Mắt trái
  // Đường kính mống mắt
  right_eye_iris_diameter: "", // Mắt phải
  left_eye_iris_diameter: "", // Mắt trái
  // Kích thước đồng tử
  right_eye_pupil_size: "", // Mắt phải
  left_eye_pupil_size: "", // Mắt trái
  // Độ sâu tiền phòng
  right_eye_anterior_chamber_depth: "", // Mắt phải
  left_eye_anterior_chamber_depth: "", // Mắt trái
  // Chiều dài trục nhãn cầu
  right_eye_eyeball_axis_length: "", // Mắt phải
  left_eye_eyeball_axis_length: "", // Mắt trái
};

export const defaultContactReExamination = {
  appointment_id: null, //id lịch hẹn, required
  optometrist: null, //id người đo
  examiner: null, //id người khám
  examination_at: null, //Ngày khám,  format: yyyy-mm-dd
  reexamination_at: null, //Ngày tái khám,  format: yyyy-mm-dd
  time_until_reexamination: "", //Số ngày đến ngày tái khám
  note: "", // Lưu ý
  cls: [], // Chỉ định CLS
  result: "", // Kết quả khám
  solution: "", // Phương án xử lý
  // Thông tin kỹ thuật
  right_eye_ktx: "", // KTX
  right_eye_orx: "", // ORx
  right_eye_shv: "", // SHV
  right_eye_eyeball_axis_length: "", // Chiều dài trục nhãn cầu
  left_eye_ktx: "", // KTX
  left_eye_orx: "", // ORx
  left_eye_shv: "", // SHV
  left_eye_eyeball_axis_length: "", // Chiều dài trục nhãn cầu
  // Đơn thuốc
  prescription: [],
};

export const defaultVisualExamination = {
  appointment_id: null, //id lịch hẹn, required
  optometrist: null, //id người đo
  examiner: null, //id người khám
  examination_at: null, //Ngày khám,  format: yyyy-mm-dd
  reexamination_at: null, //Ngày tái khám,  format: yyyy-mm-dd
  time_until_reexamination: "", //Số ngày đến ngày tái khám
  reason: "", // Lý do khám, required
  note: "", // Lưu ý
  cls: [], // Chỉ định CLS
  result: "", // Kết quả khám
  solution: "", // Xử lý và tư vấn

  prescription: [], // Đơn thuốc

  // Khám lâm sàng
  right_eye_close_without_glasses: "", // Gần không kính
  right_eye_far_without_glasses: "", // Xa không kính
  right_eye_close_old_glasses: "", // Gần kính cũ
  right_eye_far_old_glasses: "", // Xa kính cũ
  right_eye_sbdt: "", // SBĐT
  right_eye_subjective_refraction: "", // Khúc xạ chủ quan
  right_eye_contrast: "", // Thị lực tương phản
  right_eye_with_glare: "", // Thị lực với ánh sáng chói

  left_eye_close_without_glasses: "", // Gần không kính
  left_eye_far_without_glasses: "", // Xa không kính
  left_eye_close_old_glasses: "", // Gần kính cũ
  left_eye_far_old_glasses: "", // Xa kính cũ
  left_eye_sbdt: "", // SBĐT
  left_eye_subjective_refraction: "", // Khúc xạ chủ quan
  left_eye_contrast: "", // Thị lực tương phản
  left_eye_with_glare: "", // Thị lực với ánh sáng chói

  eyes_close_without_glasses: "", // Gần không kính
  eyes_far_without_glasses: "", // Xa không kính
  eyes_close_old_glasses: "", // Gần kính cũ
  eyes_far_old_glasses: "", // Xa kính cũ
  eyes_sbdt: "", // SBĐT
  eyes_subjective_refraction: "", // Khúc xạ chủ quan
  right_left_eye_add: "", // Phải - trái ADD
  eyes_add: "", // ADD
  eyes_contrast: "", // Thị lực tương phản
  eyes_with_glare: "", // Thị lực với ánh sáng chói
  // Sắc giác
  color_sense_mp: "", // MP
  color_sense_mt: "", // MT
  color_sense_test: "", // Test
  // NPC
  npc_mp: "", // MP
  npc_mt: "", // MT
  npc_test: "", // Test
  eoms: "", // EOMs
  // KCDT
  kcdt_close: "", // Gần
  kcdt_far: "", // Xa
  pupil: "", //
  light_perrl: "", // Perrl sáng
  dark_perrl: "", // Perrl tối

  // Cover test
  cover_test_dsc: "", //
  cover_test_dcc: "", //
  cover_test_nsc: "", //
  cover_test_ncc: "", //
  // Thị trường
  mp_exam: "", //
  mt_exam: "", //
  fas: "", // FAS
  ffs: "", // FFS
  fvs: "", // FVS

  // Đánh giá khiếm thị
  //Trợ cụ đang sử dụng
  tool_in_use_name: "", // Tên
  tool_in_use_wattage: "", // Công suất
  tool_in_use_right_eye: "", // Mắt phải
  tool_in_use_left_eye: "", // Mắt trái
  tool_in_use_status: "", // Tình trạng
  // Trợ cụ nhìn gần
  close_up_tool_name: "", // Tên
  close_up_tool_wattage: "", // Công suất
  close_up_tool_right_eye: "", // Mắt phải
  close_up_tool_left_eye: "", // Mắt trái
  close_up_tool_status: "", // Tình trạng
  // Trợ cụ nhìn xa
  foresight_tool_name: "", // Tên
  foresight_tool_wattage: "", // Công suất
  foresight_tool_right_eye: "", // Mắt phải
  foresight_tool_left_eye: "", // Mắt trái
  foresight_tool_status: "", // Tình trạng
  // Trợ cụ phi quang học
  non_optical_tool_name: "", // Tên
  non_optical_tool_wattage: "", // Công suất
  non_optical_tool_right_eye: "", // Mắt phải
  non_optical_tool_left_eye: "", // Mắt trái
  non_optical_tool_status: "", // Tình trạng

  // Đơn kính
  right_eye_glasses_prescription: "", // Mắt phải
  left_eye_glasses_prescription: "", // Mắt trái
};
