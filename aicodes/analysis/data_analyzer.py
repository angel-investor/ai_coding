"""
数据分析器
生成交互式HTML数据分析报告
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Optional


class DataAnalyzer:
    """数据分析器类"""
    
    def __init__(self, data_path: str):
        """
        初始化数据分析器
        
        Args:
            data_path: 数据集路径
        """
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
        
    def load_data(self) -> pd.DataFrame:
        """
        加载数据集
        
        Returns:
            DataFrame: 加载的数据
        """
        if self.data_path.endswith('.xlsx'):
            self.df = pd.read_excel(self.data_path)
        elif self.data_path.endswith('.csv'):
            self.df = pd.read_csv(self.data_path)
        else:
            raise ValueError("不支持的文件格式")
        
        return self.df
    
    def generate_basic_stats(self) -> dict:
        """
        生成基础统计信息
        
        Returns:
            dict: 统计信息字典
        """
        if self.df is None:
            self.load_data()
        
        stats = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'missing': self.df.isnull().sum().to_dict(),
            'describe': self.df.describe().to_dict()
        }
        
        return stats
    
    def plot_distribution(self, column: str) -> go.Figure:
        """
        绘制特征分布图
        
        Args:
            column: 列名
            
        Returns:
            Figure: Plotly图表对象
        """
        if self.df is None:
            self.load_data()
        
        fig = px.histogram(self.df, x=column, title=f'{column} 分布图')
        return fig
    
    def plot_correlation_matrix(self) -> go.Figure:
        """
        绘制相关性矩阵热力图
        
        Returns:
            Figure: Plotly图表对象
        """
        if self.df is None:
            self.load_data()
        
        # 只选择数值列
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        corr_matrix = self.df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            title='特征相关性矩阵',
            color_continuous_scale='RdBu_r'
        )
        
        return fig
    
    def plot_target_distribution(self, target_col: str) -> go.Figure:
        """
        绘制目标变量分布
        
        Args:
            target_col: 目标列名
            
        Returns:
            Figure: Plotly图表对象
        """
        if self.df is None:
            self.load_data()
        
        value_counts = self.df[target_col].value_counts()
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f'{target_col} 分布'
        )
        
        return fig
    
    def generate_html_report(self, output_path: str = 'analysis_report.html'):
        """
        生成完整的HTML分析报告
        
        Args:
            output_path: 输出HTML文件路径
        """
        if self.df is None:
            self.load_data()
        
        # 创建子图
        from plotly.subplots import make_subplots
        
        # 这里可以组合多个图表生成完整报告
        # 示例：生成多个图表并保存为HTML
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>心血管疾病数据分析报告</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                }}
                .chart {{
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>心血管疾病数据分析报告</h1>
                <div id="charts"></div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"分析报告已生成: {output_path}")
