# mental_arithmetic

## Plan

1.	增加更多运算，如power和log
2.	增加混合运算
3.  增加configuration，方便调整难度
4.	增加文件读写记录，记录每次做题的成绩和做错的题，方便复盘
5.	每道题做完后都显示一下剩余时间、做对的和总题目数量
6.	把口算程序做成一个指令，在terminal中可以直接使用
7.  热身功能
8.  图形化UI
9.  Test case

## Design

### 菜单menu

- options: 
    - stopwatch
        - fixed duration
        - 1min, 3min[Default], 5min
    - timer
        - fixed number of questions
        - record the timer
    - zen
        - quit, 记录
- Generate Question
- Input
- Compare Result
- Record Score

### Test case

## Notes
- .src 两个commit合在一起
- main先不commit



'''
- options: 
    - stopwatch
        - fixed duration
        - settings: 1min, 3min[Default], 5min
    - timer
        - fixed number of questions
        - record the timer
    - zen
        - quit, 记录
    - settings
- Generate Question
- Input
- Compare Result
- Record Score

Questions, correspond answer and timestamp
Start 
time
Mode
'''