from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox

class TicTacToe(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("圈圈叉叉")
        
        # 棋盤初始狀態
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"  # 當前玩家
        
        # 建立 UI
        self.layout = QGridLayout()
        self.buttons = [[QPushButton("") for _ in range(3)] for _ in range(3)]
        self.setup_ui()
        
        self.setLayout(self.layout)
    
    def setup_ui(self):
        """初始化棋盤按鈕佈局"""
        for row in range(3):
            for col in range(3):
                button = self.buttons[row][col]
                button.setFixedSize(100, 100)
                button.clicked.connect(lambda _, r=row, c=col: self.handle_click(r, c))
                self.layout.addWidget(button, row, col)
    
    def handle_click(self, row, col):
        """處理按鈕點擊事件"""
        # 如果該位置已被佔用，直接返回
        if self.board[row][col] != " ":
            QMessageBox.information(self, "提示", "該位置已被佔用！")
            return
        
        # 更新棋盤與按鈕
        self.board[row][col] = self.current_player
        self.buttons[row][col].setText(self.current_player)
        self.buttons[row][col].setEnabled(False)  # 禁用已點擊的按鈕
        
        # 檢查勝負或平局
        winner = self.check_winner()
        if winner:
            QMessageBox.information(self, "遊戲結束", f"玩家 {winner} 獲勝！")
            self.reset_game()
            return
        
        if self.check_draw():
            QMessageBox.information(self, "遊戲結束", "平局！")
            self.reset_game()
            return
        
        # 切換玩家
        self.current_player = "O" if self.current_player == "X" else "X"
    
    def check_winner(self):
        """檢查是否有玩家獲勝"""
        for i in range(3):
            # 檢查行與列
            if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] != " ":
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] != " ":
                return self.board[0][i]
        
        # 檢查對角線
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != " ":
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != " ":
            return self.board[0][2]
        
        return None
    
    def check_draw(self):
        """檢查是否平局"""
        return all(cell != " " for row in self.board for cell in row)
    
    def reset_game(self):
        """重置遊戲狀態"""
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        for row in range(3):
            for col in range(3):
                button = self.buttons[row][col]
                button.setText("")
                button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = TicTacToe()
    window.show()
    app.exec()
