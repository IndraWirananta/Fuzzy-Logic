from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


#fungsi untuk mencari y axis dari key di dalam fungsi keanggotaan segitiga
def triangle(key, points):
    a = points[0]
    b = points[1]
    c = points[2]
    output = 0
    if key >= a and key <= b:
        output = (key - a) / (b - a)
    elif key > b and key <= c:
        output = (c - key) / (c - b)
    else:
        output = 0
    return output


#fungsi untuk mencari y axis dari key di dalam fungsi keanggotaan trapesium
def trapezoid(key, points):
    a = points[0]
    b = points[1]
    c = points[2]
    d = points[3]
    output = 0
    if key > a and key < b:
        output = (key - a) / (b - a)
    elif key >= b and key <= c:
        output = 1
    elif key > c and key < d:
        output = (d - key) / (d - c)
    else:
        output = 0
    return output


#membentuk plot segitiga untuk defuzzifikasi mamdani
def createTrianglePlot(ncoor, points):
    plots = [0] * (ncoor)
    a = points[0]
    b = points[1]
    c = points[2]
    for i in range(a, b):
        plots[i] = (i - a) / (b - a)
    for i in range(b, c):
        plots[i] = (c - i) / (c - b)
    return plots


#membentuk plot trapesium untuk defuzzifikasi mamdani
def createTrapezoidPlot(ncoor, points):
    plots = [0] * (ncoor)
    a = points[0]
    b = points[1]
    c = points[2]
    d = points[3]
    for i in range(a, b):
        plots[i] = (i - a) / (b - a)
    for i in range(b, c):
        plots[i] = 1
    for i in range(c, d):
        plots[i] = (d - i) / (d - c)
    return plots


#mencari center of grafity proses defuzzifikasi mamdani
# dari plot yang sudah digabungkan
def centerOfGravity(aggregatedPlots):
    n = len(aggregatedPlots)
    xAxis = list(range(n))
    centroidNum = 0
    centroidDenum = 0
    for i in range(n):
        centroidNum += xAxis[i] * aggregatedPlots[i]
        centroidDenum += aggregatedPlots[i]
    return (centroidNum / centroidDenum)


#fungsi mengambil data
def getdata():
    xlsx = pd.read_excel('input.xlsx')
    return xlsx


#menyimpan data
xlsx = getdata()
xlsx_output = getdata()

#klasifikasi untuk lembur
fuzzyOvertimeLow = [0, 0, 7, 10]  #bentuk trapesium
fuzzyOvertimeMedium = [7, 10, 15, 17]  #bentuk trapesium
fuzzyOvertimeMediumhigh = [15, 17, 20, 25]  #bentuk trapesium
fuzzyOvertimeHigh = [20, 25, 30, 30]  #bentuk trapesium

#klasifikasi untuk gaji
fuzzyWageLow = [7, 7, 8, 12]  #bentuk trapesium
fuzzyWageMedium = [8, 12, 15]  #bentuk segitiga
fuzzyWageHigh = [12, 15, 28, 28]  #bentuk trapesium


#digunakan untuk menentukan rule/aturan inferensi
#dan fuzzifikasi berdasarkan jam lembur dan gaji
def evaluateRules(overtime, wage):
    rules = [[0, 0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0]]

    #hasil fuzzyfikasi lembur
    #dibagi menjadi 4 input linguistik
    resultOTlow = trapezoid(overtime, fuzzyOvertimeLow)
    resultOTmedium = trapezoid(overtime, fuzzyOvertimeMedium)
    resultOTmediumhigh = trapezoid(overtime, fuzzyOvertimeMediumhigh)
    resultOThigh = trapezoid(overtime, fuzzyOvertimeHigh)

    #hasil fuzzyfikasi gaji
    #dibagi menjadi 3 input linguistik
    resultWageLow = trapezoid(wage, fuzzyWageLow)
    resultWageMedium = triangle(wage, fuzzyWageMedium)
    resultWageHigh = trapezoid(wage, fuzzyWageHigh)

    # RULE 1, input lembur low dengan gaji medium,
    # luaran low
    rules[0][0] = min(resultOTlow, resultWageMedium)
    # RULE 2, input lembur low dengan gaji high,
    # luaran low
    rules[0][1] = min(resultOTlow, resultWageHigh)
    # RULE 3, input lembur medium dengan gaji high,
    # luaran low
    rules[0][2] = min(resultOTmedium, resultWageHigh)

    # RULE 4, input lembur medium dengan gaji medium,
    # luaran medium
    rules[1][0] = min(resultOTmedium, resultWageMedium)
    # RULE 5, input lembur low dengan gaji low,
    # luaran medium
    rules[1][1] = min(resultOTlow, resultWageLow)
    # RULE 6, input lembur mediumhigh dengan gaji high,
    # luaran medium
    rules[1][2] = min(resultOTmediumhigh, resultWageHigh)

    # RULE 7, input lembur mediumhigh dengan gaji low,
    # luaran high
    rules[2][0] = min(resultOTmediumhigh, resultWageLow)
    # RULE 8, input lembur mediumhigh dengan gaji medium,
    # luaran high
    rules[2][1] = min(resultOTmediumhigh, resultWageMedium)
    # RULE 9, input lembur high dengan gaji high,
    # luaran high
    rules[2][2] = min(resultOThigh, resultWageHigh)
    # RULE 10, input lembur medium dengan gaji low,
    # luaran high
    rules[2][3] = min(resultOTmedium, resultWageLow)

    # RULE 11, input lembur high dengan gaji low,
    # luaran veryhigh
    rules[3][0] = min(resultOThigh, resultWageLow)
    # RULE 12, input lembur high dengan gaji medium,
    # luaran veryhigh
    rules[3][1] = min(resultOThigh, resultWageMedium)
    return rules


#penggabungan plot low,medium,high,veryhigh menjadi 1 plot agregat
#yang kemudian didefuzzifikasi berdasarkan hasil
#yang didapatkan dari rules
def plotAggregation(rules, low, med, high, veryhigh):
    result = [0] * 200
    nlow = np.max(rules[0])
    nmed = np.max(rules[1])
    nhigh = np.max(rules[2])
    nveryhigh = np.max(rules[3])
    for i in range(len(result)):
        if nlow > 0 and i <= 60:
            result[i] = min(nlow, low[i])
        if nmed > 0 and i >= 30 and i <= 100:
            result[i] = max(min(nmed, med[i]), result[i])
        if nhigh > 0 and i >= 60 and i <= 150:
            result[i] = max(min(nhigh, high[i]), result[i])
        if nveryhigh > 0 and i >= 100 and i <= 200:
            result[i] = max(min(nveryhigh, veryhigh[i]), result[i])

    return result


#pembuatan plot trapesium untuk bonus low
def fuzzyBonusLow():
    return createTrapezoidPlot(200, [0, 0, 30, 60])


#pembuatan plot trapesium untuk bonus medium
def fuzzyBonusMed():
    return createTrianglePlot(200, [30, 60, 100])


#pembuatan plot trapesium untuk bonus high
def fuzzyBonusHigh():
    return createTrianglePlot(200, [60, 100, 150])


#pembuatan plot trapesium untuk bonus very high
def fuzzyBonusVeryHigh():
    return createTrapezoidPlot(200, [100, 150, 200, 200])


#main program
def main():
    array = []  #menyimpan hasil fuzzylogic masing-masing row xlsx
    for i in range(200):
        rules = evaluateRules(xlsx.iloc[i]['WaktuLembur'],
                              xlsx.iloc[i]['TotalGaji (Dalam Juta Rupiah)'])
        aggregateValues = plotAggregation(rules, fuzzyBonusLow(),
                                          fuzzyBonusMed(), fuzzyBonusHigh(),
                                          fuzzyBonusVeryHigh())
        centroid = centerOfGravity(aggregateValues)
        #karena defuzzifikasi menggunakan keanggotaan sepanjang 200 indeks, dan bonus maksimal yang diberikan
        #adalah 5 juta, maka hasil dari centerofgrafity akan dibagi 40. (satuan output adalah juta rupiah)
        array.append(round(centroid / 40, 4))
        print(f'no {i+1} :', round(centroid / 40, 4), ' juta rupiah')
    #memasukan hasil fuzzylogic kedalam xlsx
    xlsx_output.insert(5, "BantuanTunai (dalam juta rupiah)", array, True)
    xlsx_output.sort_values("BantuanTunai (dalam juta rupiah)",
                            ascending=False,
                            inplace=True)
    xlsx_output.to_excel('./output.xlsx', index=False)
    xlsx_output.head(10).to_excel('./output_top_10.xlsx', index=False)


if __name__ == "__main__":
    main()
