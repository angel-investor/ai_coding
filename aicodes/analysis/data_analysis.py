"""
心血管疾病数据分析
生成交互式 HTML 报告
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

# 设置日志
logger = setup_logger('analysis', log_dir='./logs')


class CardiovascularDataAnalysis:
    """心血管疾病数据分析类"""
    
    def __init__(self, data_path: str):
        """
        初始化分析器
        
        Args:
            data_path: 数据文件路径
        """
        self.data_path = data_path
        self.df = None
        self.stats = {}
        self.figures = {}
        
        logger.info(f"初始化数据分析器，数据路径: {data_path}")
    
    def load_data(self):
        """加载并预处理数据"""
        logger.info("开始加载数据...")
        
        try:
            # 加载数据
            if self.data_path.endswith('.xlsx'):
                self.df = pd.read_excel(self.data_path)
            elif self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            else:
                raise ValueError("不支持的文件格式，请使用 .xlsx 或 .csv")
            
            logger.info(f"数据加载成功，形状: {self.df.shape}")
            
            # 检查缺失值
            missing_values = self.df.isnull().sum()
            if missing_values.sum() > 0:
                logger.warning(f"发现缺失值:\n{missing_values[missing_values > 0]}")
                
                # 处理缺失值：数值列用均值填充
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if self.df[col].isnull().sum() > 0:
                        mean_value = self.df[col].mean()
                        self.df[col].fillna(mean_value, inplace=True)
                        logger.info(f"列 {col} 的缺失值已用均值 {mean_value:.2f} 填充")
            else:
                logger.info("数据无缺失值")
            
            return self.df
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise
    
    def generate_basic_stats(self):
        """生成基础统计信息"""
        logger.info("生成基础统计信息...")
        
        self.stats = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'describe': self.df.describe().to_dict(),
            'missing': self.df.isnull().sum().to_dict(),
            'cardio_distribution': self.df['cardio'].value_counts().to_dict() if 'cardio' in self.df.columns else {}
        }
        
        logger.info(f"数据集包含 {self.stats['shape'][0]} 行, {self.stats['shape'][1]} 列")
        
        return self.stats
    
    def plot_age_distribution(self):
        """绘制年龄分布直方图"""
        logger.info("生成年龄分布直方图...")
        
        fig = px.histogram(
            self.df,
            x='age',
            nbins=50,
            title='年龄分布直方图',
            labels={'age': '年龄', 'count': '人数'},
            color_discrete_sequence=['#667eea']
        )
        
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            showlegend=False
        )
        
        self.figures['age_distribution'] = fig
        return fig
    
    def plot_blood_pressure_boxplot(self):
        """绘制血压箱线图"""
        logger.info("生成血压箱线图...")
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('收缩压 (ap_hi)', '舒张压 (ap_lo)')
        )
        
        # 收缩压箱线图
        fig.add_trace(
            go.Box(
                y=self.df['ap_hi'],
                name='收缩压',
                marker_color='#667eea',
                boxmean='sd'
            ),
            row=1, col=1
        )
        
        # 舒张压箱线图
        fig.add_trace(
            go.Box(
                y=self.df['ap_lo'],
                name='舒张压',
                marker_color='#764ba2',
                boxmean='sd'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='血压分布箱线图',
            template='plotly_white',
            showlegend=False,
            height=500
        )
        
        fig.update_yaxes(title_text="血压值 (mmHg)", row=1, col=1)
        fig.update_yaxes(title_text="血压值 (mmHg)", row=1, col=2)
        
        self.figures['blood_pressure'] = fig
        return fig
    
    def plot_correlation_heatmap(self):
        """绘制特征与 cardio 的相关性热力图"""
        logger.info("生成相关性热力图...")
        
        # 选择数值列
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 计算相关性矩阵
        corr_matrix = self.df[numeric_cols].corr()
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="相关系数")
        ))
        
        fig.update_layout(
            title='特征相关性热力图',
            template='plotly_white',
            width=800,
            height=800,
            xaxis={'side': 'bottom'}
        )
        
        self.figures['correlation'] = fig
        return fig
    
    def plot_categorical_vs_cardio(self):
        """绘制分类特征与 cardio 的对比条形图"""
        logger.info("生成分类特征对比图...")
        
        # 定义要分析的分类特征
        categorical_features = {
            'gender': {1: '女性', 2: '男性'},
            'smoke': {0: '不吸烟', 1: '吸烟'},
            'alco': {0: '不饮酒', 1: '饮酒'},
            'active': {0: '不运动', 1: '运动'}
        }
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('性别 vs 心血管疾病', '吸烟 vs 心血管疾病',
                          '饮酒 vs 心血管疾病', '运动 vs 心血管疾病'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
        
        for idx, (feature, mapping) in enumerate(categorical_features.items()):
            if feature not in self.df.columns:
                continue
                
            # 计算每个类别中患病和不患病的人数
            cross_tab = pd.crosstab(self.df[feature], self.df['cardio'], normalize='index') * 100
            
            row, col = positions[idx]
            
            # 添加柱状图
            for cardio_val in [0, 1]:
                if cardio_val in cross_tab.columns:
                    fig.add_trace(
                        go.Bar(
                            x=[mapping.get(x, str(x)) for x in cross_tab.index],
                            y=cross_tab[cardio_val],
                            name='患病' if cardio_val == 1 else '健康',
                            marker_color=colors[idx] if cardio_val == 1 else '#e0e0e0',
                            showlegend=(idx == 0)
                        ),
                        row=row, col=col
                    )
        
        fig.update_layout(
            title_text='分类特征与心血管疾病关系',
            template='plotly_white',
            height=800,
            barmode='group'
        )
        
        fig.update_yaxes(title_text="百分比 (%)")
        
        self.figures['categorical_vs_cardio'] = fig
        return fig
    
    def plot_cardio_distribution(self):
        """绘制目标变量分布饼图"""
        logger.info("生成目标变量分布图...")
        
        cardio_counts = self.df['cardio'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=['健康', '患病'],
            values=cardio_counts.values,
            hole=0.4,
            marker_colors=['#4facfe', '#f093fb'],
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig.update_layout(
            title='心血管疾病分布',
            template='plotly_white',
            height=400
        )
        
        self.figures['cardio_distribution'] = fig
        return fig
    
    def generate_all_plots(self):
        """生成所有图表"""
        logger.info("开始生成所有图表...")
        
        self.plot_age_distribution()
        self.plot_blood_pressure_boxplot()
        self.plot_correlation_heatmap()
        self.plot_categorical_vs_cardio()
        self.plot_cardio_distribution()
        
        logger.info(f"共生成 {len(self.figures)} 个图表")
        
        return self.figures
    
    def generate_html_report(self, output_path: str = 'analysis/report.html'):
        """生成完整的交互式 HTML 报告"""
        logger.info(f"开始生成 HTML 报告: {output_path}")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 生成所有图表
        self.generate_all_plots()
        
        # 将图表转换为 HTML
        plots_html = {}
        for name, fig in self.figures.items():
            plots_html[name] = fig.to_html(
                include_plotlyjs=False,
                div_id=f'plot_{name}',
                config={'displayModeBar': True, 'responsive': True}
            )
        
        # 生成统计表格 HTML
        describe_df = pd.DataFrame(self.stats['describe'])
        stats_table_html = describe_df.to_html(
            classes='stats-table',
            float_format=lambda x: f'{x:.2f}'
        )
        
        # 生成 HTML 内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心血管疾病数据分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 
                         'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: #f5f7fa;
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 0.95em;
        }}
        
        .container {{
            display: flex;
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        .sidebar {{
            width: 250px;
            background: white;
            padding: 20px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
        }}
        
        .sidebar h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .sidebar ul {{
            list-style: none;
        }}
        
        .sidebar li {{
            margin-bottom: 10px;
        }}
        
        .sidebar a {{
            color: #555;
            text-decoration: none;
            display: block;
            padding: 8px 12px;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        
        .sidebar a:hover {{
            background: #f0f0f0;
            color: #667eea;
            transform: translateX(5px);
        }}
        
        .content {{
            flex: 1;
            padding: 30px;
        }}
        
        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-card .label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .stats-table th,
        .stats-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stats-table th {{
            background: #f8f9fa;
            color: #667eea;
            font-weight: 600;
        }}
        
        .stats-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .plot-container {{
            margin: 30px 0;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🫀 心血管疾病数据分析报告</h1>
        <div class="meta">
            生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            数据集: {os.path.basename(self.data_path)}
        </div>
    </div>
    
    <div class="container">
        <nav class="sidebar">
            <h3>📋 目录导航</h3>
            <ul>
                <li><a href="#overview">数据概览</a></li>
                <li><a href="#statistics">基础统计</a></li>
                <li><a href="#cardio-dist">疾病分布</a></li>
                <li><a href="#age-dist">年龄分布</a></li>
                <li><a href="#blood-pressure">血压分析</a></li>
                <li><a href="#correlation">相关性分析</a></li>
                <li><a href="#categorical">分类特征分析</a></li>
            </ul>
        </nav>
        
        <main class="content">
            <!-- 数据概览 -->
            <section id="overview" class="section">
                <h2>📊 数据概览</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">总样本数</div>
                        <div class="value">{self.stats['shape'][0]:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">特征数量</div>
                        <div class="value">{self.stats['shape'][1]}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">患病人数</div>
                        <div class="value">{self.stats['cardio_distribution'].get(1, 0):,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">健康人数</div>
                        <div class="value">{self.stats['cardio_distribution'].get(0, 0):,}</div>
                    </div>
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    本数据集包含 <strong>{self.stats['shape'][0]:,}</strong> 个样本，
                    共 <strong>{self.stats['shape'][1]}</strong> 个特征。
                    数据集用于预测心血管疾病，目标变量为 <code>cardio</code>（0=健康，1=患病）。
                </p>
            </section>
            
            <!-- 疾病分布 -->
            <section id="cardio-dist" class="section">
                <h2>🎯 疾病分布</h2>
                <div class="plot-container">
                    {plots_html['cardio_distribution']}
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    数据集中患病样本占比为 
                    <strong>{self.stats['cardio_distribution'].get(1, 0) / self.stats['shape'][0] * 100:.1f}%</strong>，
                    健康样本占比为 
                    <strong>{self.stats['cardio_distribution'].get(0, 0) / self.stats['shape'][0] * 100:.1f}%</strong>。
                </p>
            </section>
            
            <!-- 基础统计 -->
            <section id="statistics" class="section">
                <h2>📈 基础统计信息</h2>
                {stats_table_html}
            </section>
            
            <!-- 年龄分布 -->
            <section id="age-dist" class="section">
                <h2>👥 年龄分布</h2>
                <div class="plot-container">
                    {plots_html['age_distribution']}
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    年龄分布显示了样本的年龄结构。可以看出数据集中不同年龄段的人群分布情况。
                </p>
            </section>
            
            <!-- 血压分析 -->
            <section id="blood-pressure" class="section">
                <h2>💓 血压分析</h2>
                <div class="plot-container">
                    {plots_html['blood_pressure']}
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    箱线图展示了收缩压和舒张压的分布情况，包括中位数、四分位数和异常值。
                    可以帮助识别血压异常的样本。
                </p>
            </section>
            
            <!-- 相关性分析 -->
            <section id="correlation" class="section">
                <h2>🔗 特征相关性分析</h2>
                <div class="plot-container">
                    {plots_html['correlation']}
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    相关性热力图展示了各特征之间的线性相关关系。
                    颜色越深表示相关性越强，红色表示正相关，蓝色表示负相关。
                </p>
            </section>
            
            <!-- 分类特征分析 -->
            <section id="categorical" class="section">
                <h2>📊 分类特征与疾病关系</h2>
                <div class="plot-container">
                    {plots_html['categorical_vs_cardio']}
                </div>
                <p style="margin-top: 20px; line-height: 1.8;">
                    该图展示了性别、吸烟、饮酒、运动等分类特征与心血管疾病的关系。
                    可以看出不同生活习惯对患病风险的影响。
                </p>
            </section>
        </main>
    </div>
    
    <div class="footer">
        <p>© 2024 心血管疾病预测系统 | 数据分析报告</p>
        <p>Powered by Python + Pandas + Plotly</p>
    </div>
</body>
</html>
"""
        
        # 保存 HTML 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML 报告已生成: {output_path}")
        logger.info(f"报告大小: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        return output_path


def main():
    """主函数"""
    # 数据路径
    data_path = "D:/project/workspace/ai_coding/data/心血管疾病.xlsx"
    
    # 创建分析器
    analyzer = CardiovascularDataAnalysis(data_path)
    
    # 加载数据
    analyzer.load_data()
    
    # 生成基础统计
    analyzer.generate_basic_stats()
    
    # 生成 HTML 报告
    report_path = analyzer.generate_html_report('analysis/report.html')
    
    logger.info("=" * 50)
    logger.info("数据分析完成！")
    logger.info(f"报告位置: {os.path.abspath(report_path)}")
    logger.info("=" * 50)
    
    print("\n" + "=" * 50)
    print("✅ 数据分析完成！")
    print(f"📊 报告已生成: {os.path.abspath(report_path)}")
    print("💡 请用浏览器打开 report.html 查看完整报告")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()

