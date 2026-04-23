import ast
import operator
import math

class SafeCalculator:
    """
    安全な数式評価を目的とした電卓クラス
    - evalは使用せず、astで構文解析
    - 許可したノードのみ実行して安全性を確保
    """

    def __init__(self):
        self.history=[]
        self.last_result=None

        # 許可する演算子(ホワイトリスト)
        self.operators={
            ast.Add:operator.add,
            ast.Sub:operator.sub,
            ast.Mult:operator.mul,
            ast.Div:operator.truediv,
            ast.Pow:operator.pow,
        }

        # 関数は(関数本体 + 引数数)で管理(誤使用防止)
        self.functions={
            "sqrt":(math.sqrt,1),
            "sin":(math.sin,1),
            "cos":(math.cos,1),
            "tan":(math.tan,1),
            "log":(math.log,(1,2)), # log(x) or log(x,base)
            "exp":(math.exp,1),
            "abs":(abs,1),
            "round":(round,(1,2)), # round(x) or round(x,n)
        }

        # 許可する定数のみ使用可能
        self.constants={
            "pi":math.pi,
            "e":math.e,
        }

    def evaluate(self,expr:str):
        """
        ユーザー入力の数式を安全に評価する
        """

        # 前回結果(ana)の置換
        if self.last_result is not None:
            expr=expr.replace("ana",str(self.last_result))

        try:
            node=ast.parse(expr,mode="eval")
            result=self._eval(node.body)

            self.last_result=result
            self.history.append(f"{expr}={result}")
            return result
        
        except ZeroDivisionError:
            return"0では割れません"
        except SyntaxError:
            return"構文が正しくありません"
        except ValueError as e:
            return f"エラー:{e}"
        except Exception as e:
            # 想定外のエラーも可視化(デバックしやすくする)
            return f"予期しないエラー:{e}"
        
    def _eval(self,node):
        """
        ASTノードを再起的に評価する内部関数

        許可されたノードのみ処理し、それ以外は例外を
        投げることで安全性を担保
        """

        if isinstance(node,ast.Constant):
            if isinstance(node.value,(int,float)):
                return node.value
            raise ValueError("数値意外は使用できません")
        
        elif isinstance(node,ast.BinOp):
            # 未許可の演算子は実行しない(安全性のため)
            if type(node.op) not in self.operators:
                raise ValueError("許可されていない演算子です")
            
            return self.operators[type(node.op)](
                self._eval(node.left),
                self._eval(node.right),
            )
        
        elif isinstance(node,ast.UnaryOp):
            return -self._eval(node.operand)
        
        elif isinstance(node,ast.Call):
            # 関数呼び出しはNane型のみ許可(属性アクセスなどを防ぐ)
            if not isinstance(node.func,ast.Name):
                raise ValueError("無効な呼び出しです")
            
            func_name=node.func.id

            if func_name not in self.functions:
                raise ValueError(f"許可されていない関数:{func_name}")
            
            func,arg_spec=self.functions[func_name]
            args=[self._eval(arg) for arg in node.args]
        
        # 引数の数をチェックして誤使用を防ぐ
            if isinstance(arg_spec,int):
                if len(args) !=arg_spec:
                    raise ValueError(f"{func_name}は{arg_spec}個の引数が必要です")
            elif isinstance(arg_spec,tuple):
                if len(args) not in arg_spec:
                    raise ValueError(f"{func_name}の引数は{arg_spec}個に対応しています")
            
            return func(*args)
    
        elif isinstance(node,ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            raise ValueError(f"未定義の名前:{node.id}")
        
        else:
            raise ValueError(f"無効な式:{type(node).__name__}")
        
    def show_history(self):
        if not self.history:
            print("履歴がありません")
        else:
            print("履歴:")
            for item in self.history:
                print(item)

    def clear_history(self):
        self.history.clear()
        print("履歴を削除しました")

    def show_last(self):
        if self.last_result is None:
            print("まだ計算結果がありません")
        else:
            print("最後の結果:",self.last_result)

def main():
    calc=SafeCalculator()

    print("===安全な電卓===")
    print("例:2+3*4,sqrt(16),sin(pi/2)")
    print("コマンド:history/clear/last/exit")

    while True:
        expr=input(">>>")

        if expr=="exit":
            break
        elif expr=="history":
            calc.show_history()
            continue
        elif expr=="clear":
            calc.clea_history()
            continue
        elif expr=="last":
            calc.show_last()
            continue

        result=calc.evaluate(expr)
        print("結果:",result)

if __name__=="__main__":
    main()
