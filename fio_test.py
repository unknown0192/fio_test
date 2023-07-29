#!/usr/bin/env python3
import subprocess
import time
import re
import os
from datetime import datetime
TEST_FStype = 'xfs'  ##테스트 진행한 파일시스템명을 기록하기 위한 설정 단순기록용
mixtest = 1

def wait_for_low_load():
    while os.getloadavg()[0] > 5:
        time.sleep(10)  # Wait for 10 seconds
        print(os.getloadavg()[0],"high load,,, calm down")


def run_fio_test(size, rw_option):
    # fio command and options
    command = "fio"
    options = [
        "--name=my_test",
        "--ioengine=sync"
	"--direct=1",#캐시 disable
        "--rw={}".format(rw_option),
        "--bs=4k",
        "--size={}".format(size),
        "--numjobs=10",
        "--time_based",
        "--runtime=10s",
	"--group_reporting",
        "--directory=/mnt/testdir"
    ]

    # Execute the command
    full_command = [command] + options
    process = subprocess.Popen(full_command, stdout=subprocess.PIPE)

    
    # Wait load avg
    wait_for_low_load()

    # Collect the result
    output, _ = process.communicate()
    result = output.decode("utf-8")
    return result
def run_fio_mix_test(size, rw_option, read_ratio, write_ratio):
    # fio command and options
    command = "fio"
    options = [
        "--name=my_test",
        "--ioengine=sync"
	"--direct=1",#캐시 disable
        "--rw={}".format(rw_option),
        "--rwmixread={}".format(read_ratio),
        "--rwmixwrite={}".format(write_ratio),
        "--bs=4k",
        "--size={}".format(size),
        "--numjobs=10",
        "--time_based",
        "--runtime=10s",
	"--group_reporting",
        "--directory=/mnt/testdir"
    ]

    # Execute the command
    full_command = [command] + options
    process = subprocess.Popen(full_command, stdout=subprocess.PIPE)

    # Wait for the process to complete
    #process.wait() #numjobs 상승시 계속 딜레이되는것으로 보임
    
    # Wait load avg
    wait_for_low_load()

    # Collect the result
    output, _ = process.communicate()
    result = output.decode("utf-8")
    return result


def run_tests():
    iops_pattern = r'IOPS=([\d.]+)[k]?'
    bw_pattern = r'BW=([\d.]+)[KMGT]?[i]?B/s'
    read_iops_pattern = r'read: IOPS=([\d.]+)[k]?'
    read_bw_pattern = r'READ: bw=([\d.]+)[KMGT]?[i]?B/s'
    write_iops_pattern = r'write: IOPS=([\d.]+)[k]?'
    write_bw_pattern = r'WRITE: bw=([\d.]+)[KMGT]?[i]?B/s'
    bw_unit = "MB/s"
    sizes = range(10, 11, 10) ##범위 지정 10k ~100k 10k씩 증가
    rw_options = ["read", "write", "randread", "randwrite"]
    mix_rw_options = ["rw","randrw"]
    mix_read_ratio = 60 ##read ratio
    mix_write_ratio = 40 ##write ratio
    num_iterations = 1
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.txt"
    with open(filename, "w") as file:
        for size in sizes:
            file.write("FSType : %s\n" % (TEST_FStype))
            read_iops_values = []
            read_bw_values = []
            write_iops_values = []
            write_bw_values = []
            randread_iops_values = []
            randread_bw_values = []
            randwrite_iops_values = []
            randwrite_bw_values = []
            if mixtest == 1:
                for mix_rw_option in mix_rw_options:
                    for _ in range(num_iterations):
                        result = run_fio_mix_test("{}k".format(size),mix_rw_option, mix_read_ratio, mix_write_ratio )
                        data = result
                        read_iops_match = re.search(read_iops_pattern, data)
                        write_iops_match = re.search(write_iops_pattern, data)
                        read_bw_match = re.search(read_bw_pattern, data)
                        write_bw_match = re.search(write_bw_pattern, data)
                        if read_iops_match:
                            read_iops_value = float(read_iops_match.group(1))
                        if 'k' not in read_iops_match.group(0):
                            read_iops_value /= 1000
                        if read_bw_match:
                            read_bw_value = float(read_bw_match.group(1))
                        if 'K' in read_bw_match.group(0):
                            bw_unit = 'KB/s'
                        if write_iops_match:
                            write_iops_value = float(write_iops_match.group(1))
                        if 'k' not in write_iops_match.group(0):
                            write_iops_value /= 1000
                        if write_bw_match:
                            write_bw_value = float(write_bw_match.group(1))
                        if 'K' in write_bw_match.group(0):
                            bw_unit = 'KB/s'
                        if mix_rw_option == "rw":
                            read_iops_values.append(read_iops_value)
                            read_bw_values.append(read_bw_value)
                            write_iops_values.append(write_iops_value)
                            write_bw_values.append(write_bw_value)
                        if mix_rw_option == "randrw":
                            randread_iops_values.append(read_iops_value)
                            randread_bw_values.append(read_bw_value)
                            randwrite_iops_values.append(write_iops_value)
                            randwrite_bw_values.append(write_bw_value)
                    # Calculate the average values
		            # Write results to file
                file.write("Size : %sk , RW : Mix rw Test result\n" % (size))
                avg_read = sum(read_bw_values) / len(read_bw_values)
                avg_read_iops = sum(read_iops_values) / len(read_iops_values)
                avg_write = sum(write_bw_values) / len(write_bw_values)
                avg_write_iops = sum(write_iops_values) / len(write_iops_values)
                avg_randread = sum(randread_bw_values) / len(randread_bw_values)
                avg_randread_iops = sum(randread_iops_values) / len(randread_iops_values)
                avg_randwrite = sum(randwrite_bw_values) / len(randwrite_bw_values)
                avg_randwrite_iops = sum(randwrite_iops_values) / len(randwrite_iops_values)
                file.write("BW Average Read : {:.2f} %s\n".format(avg_read) % (bw_unit))
                file.write("IOPS Average Read : {:.2f} k\n".format(avg_read_iops))
                file.write("BW Average Write : {:.2f} %s\n".format(avg_write)% (bw_unit))
                file.write("IOPS Average Read : {:.2f} k\n".format(avg_write_iops))
                file.write("BW Average RandomRead : {:.2f} %s\n".format(avg_randread)% (bw_unit))
                file.write("IOPS Average RandomRead : {:.2f} k\n".format(avg_randread_iops))
                file.write("BW Average RandomWrite : {:.2f} %s\n".format(avg_randwrite)% (bw_unit))
                file.write("IOPS Average RandomRead : {:.2f} k\n".format(avg_randwrite_iops))
            else:
                for rw_option in rw_options:
                    for _ in range(num_iterations):
                        result = run_fio_test("{}k".format(size), rw_option)
                        data = result
                        iops_match = re.search(iops_pattern, data)
                        bw_match = re.search(bw_pattern, data)
                        if iops_match:
                            iops_value = float(iops_match.group(1))
                        if 'k' not in iops_match.group(0):
                            iops_value /= 1000
                        if bw_match:
                            bw_value = float(bw_match.group(1))
                        if rw_option == 'read':
                            read_iops_values.append(iops_value)
                            read_bw_values.append(bw_value)
                        if rw_option == 'write':
                            write_iops_values.append(iops_value)
                            write_bw_values.append(bw_value)
                        if rw_option == 'randread':
                            randread_iops_values.append(iops_value)
                            randread_bw_values.append(bw_value)
                        if rw_option == 'randwrite':
                            randwrite_iops_values.append(iops_value)
                            randwrite_bw_values.append(bw_value)
		                # Calculate the average values
		                # Write results to file
                        file.write("Size : %sk , RW : %s Test result\n" % (size, rw_option))
                        if rw_option == 'read':
                            avg_read = sum(read_bw_values) / len(read_bw_values)
                            avg_read_iops = sum(read_iops_values) / len(read_iops_values)
                            file.write("BW Average Read : {:.2f} %s\n".format(avg_read) % (bw_unit))
                            file.write("IOPS Average Read : {:.2f}\n".format(avg_read_iops))
                        if rw_option == 'write':
                            avg_write = sum(write_bw_values) / len(write_bw_values)
                            avg_write_iops = sum(write_iops_values) / len(write_iops_values)
                            file.write("BW Average Write : {:.2f} \n".format(avg_write)+bw_unit)
                            file.write("IOPS Average Write : {:.2f}\n".format(avg_write_iops))
                        if rw_option == 'randread':
                            avg_randread = sum(randread_bw_values) / len(randread_bw_values)
                            avg_randread_iops = sum(randread_iops_values) / len(randread_iops_values)
                            file.write("BW Average RandomRead : {:.2f} %s\n".format(avg_randread) % (bw_unit))
                            file.write("IOPS Average RandomRead : {:.2f}\n".format(avg_randread_iops))
                        if rw_option == 'randwrite':
                            avg_randwrite = sum(randwrite_bw_values) / len(randwrite_bw_values)
                            avg_randwrite_iops = sum(randwrite_iops_values) / len(randwrite_iops_values)
                            file.write("BW Average RandomWrite : {:.2f} %s\n".format(avg_randwrite) % (bw_unit))
                            file.write("IOPS Average RandomWrite : {:.2f}\n\n".format(avg_randwrite_iops))

    print("Results saved to", filename)


# Execute the tests
run_tests()
