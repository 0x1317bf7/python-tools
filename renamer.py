import os

def rename(path, old, new, rec = False):
    print("进入" + path)
    for file in os.listdir(path):
        p = os.path.join(path, file)
        if os.path.isfile(p):
            if file.endswith(old):
                print("将" + file + "重命名")
                os.rename(p, p[0:-len(old)] + new)
        elif rec and os.path.isdir(p):
            rename(p, old, new, rec)

def main():
    path = input("请输入文件夹路径")
    rec = True if input("是否递归?(Y/N)").lower() == "y" else False

    old = input("需要更改的后缀名?")
    new = input("更改为?")

    rename(path, old, new, rec)

if __name__ == "__main__":
    main()
