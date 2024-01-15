

if __name__ == "__main__":
    file1 = open(r"C:\Users\Brian\Desktop\Price Lab\libraries\db_library.tsv")
    file2 = open(r"C:\Users\Brian\Desktop\temp_database.tsv")

    i = 0
    while i < 5:
        i += 1
        x = file1.readline().strip().split()
        y = file2.readline().strip().split()
        matching = True
        for j in range(len(x)):
            if x[j] != y[j]:
                matching = False
                break
        if matching:
            print("Match")
        else:
            print("No match")

    file1.close()
    file2.close()
