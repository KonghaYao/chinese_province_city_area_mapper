# -*- coding: utf-8 -*-
"""
pytest 配置文件和共享 fixtures
"""

import pytest


def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line("markers", "slow: 标记运行时间较长的测试")
    config.addinivalue_line("markers", "performance: 性能测试")


@pytest.fixture(scope="session")
def performance_threshold():
    """性能测试阈值配置"""
    return {
        "max_time_per_row": 0.001,  # 每行最大处理时间 (秒)
        "min_speedup": 1.0,  # 最小加速倍数
    }
