# -*- coding: utf-8 -*-
"""
性能测试文件，用于测试地址解析功能的性能表现
"""

import time
import random
import pytest
import polars as pl
from cpca import transform, transform_polars_column


@pytest.fixture
def sample_addresses():
    """生成小量测试地址数据"""
    return [
        "上海市徐汇区虹漕路461号58号楼5楼",
        "泉州市洛江区万安塘西工业区",
        "北京市朝阳区建国门外大街1号",
        "广东省深圳市南山区科技园高新南四道18号",
        "江苏省南京市鼓楼区中山路1号",
    ]


@pytest.fixture
def sample_dataframe(sample_addresses):
    """生成测试用的 polars DataFrame"""
    return pl.DataFrame({"address": sample_addresses, "id": [1, 2, 3, 4, 5]})


def generate_test_addresses(n=100000):
    """生成测试地址数据"""
    # 一些常见的地址模板
    templates = [
        "上海市徐汇区虹漕路{}号{}号楼{}楼",
        "北京市朝阳区建国门外大街{}号",
        "广东省深圳市南山区科技园{}号",
        "江苏省南京市鼓楼区中山路{}号",
        "浙江省杭州市西湖区文三路{}号",
        "四川省成都市锦江区春熙路{}号",
        "湖北省武汉市洪山区珞喻路{}号",
        "山东省济南市历下区泉城路{}号",
        "福建省厦门市思明区中山路{}号",
        "河南省郑州市中原区中原路{}号",
        "天津市和平区南京路{}号",
        "重庆市渝中区解放碑{}号",
        "辽宁省沈阳市和平区中山路{}号",
        "陕西省西安市碑林区南院门{}号",
        "山西省太原市迎泽区柳巷{}号",
        "安徽省合肥市庐阳区阜阳路{}号",
        "江西省南昌市东湖区阳明路{}号",
        "黑龙江省哈尔滨市道里区中央大街{}号",
        "吉林省长春市朝阳区人民大街{}号",
        "云南省昆明市五华区护国路{}号",
    ]

    addresses = []
    for i in range(n):
        template = random.choice(templates)
        # 随机生成一些数字
        num1 = random.randint(1, 999)
        num2 = random.randint(1, 99)
        num3 = random.randint(1, 30)

        if "{}号{}号楼{}楼" in template:
            addr = template.format(num1, num2, num3)
        elif "号" in template:
            addr = template.format(num1)
        else:
            addr = template

        addresses.append(addr)

    return addresses


class TestTransformPolarsColumn:
    """测试 transform_polars_column 函数"""

    def test_function_exists(self):
        """测试 transform_polars_column 函数是否存在"""
        from cpca import transform_polars_column

        assert callable(transform_polars_column)

    def test_basic_functionality(self, sample_dataframe):
        """测试基本功能是否正常工作"""
        result = transform_polars_column(sample_dataframe, "address")

        # 验证结果
        assert len(result) == len(sample_dataframe)
        assert "省" in result.columns
        assert "市" in result.columns
        assert "区" in result.columns
        assert "地址" in result.columns
        assert "adcode" in result.columns

        # 验证原始列仍然存在
        assert "id" in result.columns

    def test_pos_sensitive_functionality(self, sample_dataframe):
        """测试位置敏感功能"""
        result = transform_polars_column(
            sample_dataframe, "address", pos_sensitive=True
        )

        # 验证位置列存在
        assert "省_pos" in result.columns
        assert "市_pos" in result.columns
        assert "区_pos" in result.columns

    def test_invalid_column_name(self, sample_dataframe):
        """测试无效列名"""
        with pytest.raises(ValueError, match="列 'nonexistent' 不存在"):
            transform_polars_column(sample_dataframe, "nonexistent")

    def test_invalid_dataframe_type(self):
        """测试无效的 DataFrame 类型"""
        with pytest.raises(Exception):  # 应该抛出 InputTypeNotSuportException
            transform_polars_column("not a dataframe", "column")


class TestPerformanceComparison:
    """性能对比测试"""

    @pytest.mark.slow
    @pytest.mark.parametrize("n_rows", [1000, 10000])
    def test_original_transform_performance(self, n_rows):
        """测试原始 transform 函数的性能"""
        # 生成测试数据
        addresses = generate_test_addresses(n_rows)

        # 测试解析性能
        start_time = time.time()
        result = transform(addresses)
        end_time = time.time()

        total_time = end_time - start_time

        # 验证结果
        assert len(result) == n_rows
        assert total_time > 0

        print(".2f")

    @pytest.mark.slow
    @pytest.mark.parametrize("n_rows", [1000, 10000])
    def test_polars_column_performance(self, n_rows):
        """测试 transform_polars_column 函数的性能"""
        # 生成测试数据
        addresses = generate_test_addresses(n_rows)
        df = pl.DataFrame({"address": addresses})

        # 测试解析性能
        start_time = time.time()
        result = transform_polars_column(df, "address")
        end_time = time.time()

        total_time = end_time - start_time

        # 验证结果
        assert len(result) == n_rows
        assert total_time > 0

        print(".2f")

    @pytest.mark.slow
    @pytest.mark.parametrize("n_rows", [1000, 10000])
    def test_polars_column_performance_with_pos(self, n_rows):
        """测试带位置信息的 transform_polars_column 函数的性能"""
        # 生成测试数据
        addresses = generate_test_addresses(n_rows)
        df = pl.DataFrame({"address": addresses})

        # 测试解析性能
        start_time = time.time()
        result = transform_polars_column(df, "address", pos_sensitive=True)
        end_time = time.time()

        total_time = end_time - start_time

        # 验证结果
        assert len(result) == n_rows
        assert "省_pos" in result.columns
        assert total_time > 0

        print(".2f")

    @pytest.mark.slow
    @pytest.mark.parametrize("n_rows", [100000])
    def test_large_scale_performance_comparison(self, n_rows):
        """大规模性能对比测试"""
        # 测试原始方法
        addresses = generate_test_addresses(n_rows)
        start_time = time.time()
        original_result = transform(addresses)
        original_time = time.time() - start_time

        # 测试新方法
        df = pl.DataFrame({"address": addresses})
        start_time = time.time()
        polars_result = transform_polars_column(df, "address")
        polars_time = time.time() - start_time

        # 测试带位置信息的新方法
        start_time = time.time()
        polars_pos_result = transform_polars_column(df, "address", pos_sensitive=True)
        polars_pos_time = time.time() - start_time

        # 验证结果
        assert len(original_result) == n_rows
        assert len(polars_result) == n_rows
        assert len(polars_pos_result) == n_rows

        # 输出性能对比
        print(f"\n{'=' * 60}")
        print(f"性能对比结果 ({n_rows:,}行):")
        print(f"原始 transform: {original_time:.2f}秒")
        print(f"Polars 列解析: {polars_time:.2f}秒")
        print(f"Polars 列解析(带位置): {polars_pos_time:.2f}秒")

        if polars_time < original_time:
            speedup = original_time / polars_time
            print(f"Polars 版本比原始版本快 {speedup:.2f} 倍")
        else:
            slowdown = polars_time / original_time
            print(f"Polars 版本比原始版本慢 {slowdown:.2f} 倍")

        if polars_pos_time < original_time:
            speedup_pos = original_time / polars_pos_time
            print(f"Polars 版本(带位置)比原始版本快 {speedup_pos:.2f} 倍")
        else:
            slowdown_pos = polars_pos_time / original_time
            print(f"Polars 版本(带位置)比原始版本慢 {slowdown_pos:.2f} 倍")
