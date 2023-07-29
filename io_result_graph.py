#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
# 파일 시스템과 I/O 테스트 목록
file_systems = ['zfs', 'xfs']
io_tests = ['read', 'write', 'randread', 'randwrite']

# 결과 데이터를 저장할 딕셔너리
data = {fs: {io_test: {'bandwidth': [], 'iops': []} for io_test in io_tests} for fs in file_systems}

# 텍스트 파일에서 결과 데이터 읽기
with open('test_results.txt', 'r') as file:
    lines = file.readlines()
    for line in lines:
        if line.startswith('FsType'):
            fs_type = line.split(':')[1].strip()
        elif line.startswith('Size'):
            size = int(line.split(':')[1].strip().split('k')[0])
            io_test = line.split(':')[2].strip().split(' ')[0]
        elif line.startswith('BW Average'):
            parts = line.split(':')
            bandwidth = float(parts[1].split(' ')[1].strip())
            data[fs_type][io_test]['bandwidth'].append(bandwidth)
        elif line.startswith('IOPS Average'):
            parts = line.split(':')
            iops = float(parts[1].strip())
            data[fs_type][io_test]['iops'].append(iops)


print(data)
print(data['zfs']['read']['bandwidth'])
# 그래프 그리기
for io_test in io_tests:
    plt.figure()
    x_values = np.arange(10, 61, 10)
    width = 3.75
    fig, ax = plt.subplots()
    for i, fs in enumerate(file_systems):
        y_values = data[fs][io_test]['bandwidth']
        ax.bar(x_values + i * width, y_values, width, label=fs)
    ax.set_xticks(x_values + width / 2)
    ax.set_xticklabels(x_values)
    ax.legend()
    plt.title(f'{io_test.capitalize()} Performance Comparison')
    plt.xlabel('File Size (KB)')
    plt.ylabel('Throughput (MB/s)')
    plt.grid(True)
    #plt.tight_layout()
    plt.savefig(f'{io_test}_throughput.png')
    plt.close()

    plt.figure()
    plt.title(f'{io_test.capitalize()} Performance Comparison')
    plt.xlabel('File Size (KB)')
    plt.ylabel('IOPS')
    x_values = np.arange(10, 61, 10)
    fig, ax = plt.subplots()
    for i, fs in enumerate(file_systems):
        y_values = data[fs][io_test]['iops']
        ax.bar(x_values + i * width, y_values, width, label=fs)
        
    ax.set_xticks(x_values + width / 2)
    ax.set_xticklabels(x_values)
    ax.legend()
    plt.grid(True)
    #plt.tight_layout()
    plt.savefig(f'{io_test}_iops.png')
    plt.close()
