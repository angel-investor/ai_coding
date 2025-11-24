"""
自动化 Git 提交脚本
自动添加、提交和推送代码
"""

import subprocess
import sys
from datetime import datetime
import os


def run_command(command: str, cwd: str = None) -> tuple:
    """
    执行命令
    
    Args:
        command: 命令字符串
        cwd: 工作目录
        
    Returns:
        tuple: (返回码, 输出, 错误)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, '', str(e)


def git_status(repo_path: str = '.') -> str:
    """
    获取 Git 状态
    
    Args:
        repo_path: 仓库路径
        
    Returns:
        str: 状态信息
    """
    code, output, error = run_command('git status', cwd=repo_path)
    
    if code == 0:
        return output
    else:
        return f"错误: {error}"


def git_add_all(repo_path: str = '.') -> bool:
    """
    添加所有更改
    
    Args:
        repo_path: 仓库路径
        
    Returns:
        bool: 是否成功
    """
    code, output, error = run_command('git add .', cwd=repo_path)
    
    if code == 0:
        print("✓ 已添加所有更改")
        return True
    else:
        print(f"✗ 添加失败: {error}")
        return False


def git_commit(message: str, repo_path: str = '.') -> bool:
    """
    提交更改
    
    Args:
        message: 提交信息
        repo_path: 仓库路径
        
    Returns:
        bool: 是否成功
    """
    # 转义引号
    message = message.replace('"', '\\"')
    
    code, output, error = run_command(f'git commit -m "{message}"', cwd=repo_path)
    
    if code == 0:
        print(f"✓ 提交成功: {message}")
        return True
    else:
        if "nothing to commit" in output or "nothing to commit" in error:
            print("ℹ 没有需要提交的更改")
            return True
        else:
            print(f"✗ 提交失败: {error}")
            return False


def git_push(repo_path: str = '.', branch: str = 'main') -> bool:
    """
    推送到远程仓库
    
    Args:
        repo_path: 仓库路径
        branch: 分支名
        
    Returns:
        bool: 是否成功
    """
    code, output, error = run_command(f'git push origin {branch}', cwd=repo_path)
    
    if code == 0:
        print(f"✓ 推送成功到 {branch} 分支")
        return True
    else:
        print(f"✗ 推送失败: {error}")
        return False


def auto_commit(
    message: str = None,
    repo_path: str = '.',
    push: bool = False,
    branch: str = 'main'
):
    """
    自动提交流程
    
    Args:
        message: 提交信息（如果为空则自动生成）
        repo_path: 仓库路径
        push: 是否推送到远程
        branch: 分支名
    """
    print("=" * 50)
    print("自动 Git 提交脚本")
    print("=" * 50)
    
    # 检查状态
    print("\n📊 检查 Git 状态...")
    status = git_status(repo_path)
    print(status)
    
    # 如果没有提供提交信息，自动生成
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Auto commit at {timestamp}"
    
    # 添加所有更改
    print("\n📝 添加更改...")
    if not git_add_all(repo_path):
        sys.exit(1)
    
    # 提交
    print("\n💾 提交更改...")
    if not git_commit(message, repo_path):
        sys.exit(1)
    
    # 推送（如果需要）
    if push:
        print(f"\n🚀 推送到远程 {branch} 分支...")
        if not git_push(repo_path, branch):
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ 完成!")
    print("=" * 50)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='自动化 Git 提交脚本')
    parser.add_argument('-m', '--message', type=str, help='提交信息')
    parser.add_argument('-p', '--push', action='store_true', help='推送到远程仓库')
    parser.add_argument('-b', '--branch', type=str, default='main', help='分支名（默认: main）')
    parser.add_argument('-d', '--directory', type=str, default='.', help='仓库目录（默认: 当前目录）')
    
    args = parser.parse_args()
    
    auto_commit(
        message=args.message,
        repo_path=args.directory,
        push=args.push,
        branch=args.branch
    )
