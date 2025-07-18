"""
测试包
包含所有测试模块
"""

# 测试包版本
__version__ = "1.0.0"

# 测试模块导入
from .test_database import TestDatabase
from .test_api import TestAPI, TestIntegration
from .test_security import TestSecurity, TestErrorHandling
from .test_performance import TestPerformance, TestLoadSimulation
from .test_edge_cases import TestEdgeCases, TestResourceLimits

# 测试工具导入
from .test_data_factory import TestDataFactory, TestHelpers

__all__ = [
    'TestDatabase',
    'TestAPI', 
    'TestIntegration',
    'TestSecurity',
    'TestErrorHandling',
    'TestPerformance',
    'TestLoadSimulation',
    'TestEdgeCases',
    'TestResourceLimits',
    'TestDataFactory',
    'TestHelpers'
]
