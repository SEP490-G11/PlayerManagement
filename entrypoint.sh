#!/bin/bash

# Hàm cài đặt gói nếu chưa được cài
install_if_missing() {
    local package="$1"
    local module="$2"

    if ! python3 -c "import $module" &> /dev/null; then
        echo "Đang cài đặt $package..."
        if ! pip3 install "$package"; then
            echo "Cài đặt $package thất bại" >&2
            exit 1
        fi
    fi
}

# Kiểm tra và cài đặt pymsteams nếu chưa có
install_if_missing "pymsteams" "pymsteams"

# Kiểm tra và cài đặt boto3 nếu chưa có
install_if_missing "boto3" "boto3"

# Kiểm tra và cài đặt marshmallow nếu chưa có
install_if_missing "marshmallow" "marshmallow"

# Kiểm tra và cài đặt marshmallow-objects nếu chưa có
install_if_missing "marshmallow-objects" "marshmallow-objects"

# Kiểm tra và cài đặt cachetools nếu chưa có
install_if_missing "cachetools" "cachetools"

# Kiểm tra và cài đặt apispec nếu chưa có
install_if_missing "apispec" "apispec"

# Kiểm tra và cài đặt cerberus nếu chưa có
install_if_missing "cerberus" "cerberus"

# Kiểm tra và cài đặt pyquerystring nếu chưa có
install_if_missing "pyquerystring" "pyquerystring"

# Kiểm tra và cài đặt parse-accept-language nếu chưa có
install_if_missing "parse-accept-language" "parse-accept-language"

# Kiểm tra và cài đặt payos nếu chưa có
install_if_missing "payos" "payos"

# Thực thi Odoo với các tham số được truyền vào
exec /usr/bin/odoo "$@"
