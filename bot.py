import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

EMPTY = "➖"
X = "❌"
O = "⭕"

# ===== LOGIC =====
def check_win(board, x, y, symbol):
    size = len(board)

    def count(dx, dy):
        c = 0
        i, j = x + dx, y + dy
        while 0 <= i < size and 0 <= j < size and board[i][j] == symbol:
            c += 1
            i += dx
            j += dy
        return c

    for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
        if 1 + count(dx,dy) + count(-dx,-dy) >= 5:
            return True
    return False

# ===== VIEW BUTTON =====
class CaroButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label=" ", row=x)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: CaroView = self.view

        if interaction.user != view.current_player():
            return await interaction.response.send_message("Không phải lượt bạn", ephemeral=True)

        if view.board[self.x][self.y] != EMPTY:
            return await interaction.response.send_message("Ô đã đánh", ephemeral=True)

        symbol = X if view.turn == 0 else O
        view.board[self.x][self.y] = symbol

        self.label = symbol
        self.disabled = True
        self.style = discord.ButtonStyle.danger if symbol == X else discord.ButtonStyle.success

        if check_win(view.board, self.x, self.y, symbol):
            view.disable_all_items()
            await interaction.response.edit_message(content=f"🏆 {interaction.user.mention} thắng!", view=view)
            return

        view.turn = 1 - view.turn

        await interaction.response.edit_message(
            content=f"Lượt: {view.current_player().mention}",
            view=view
        )

# ===== VIEW =====
class CaroView(discord.ui.View):
    def __init__(self, p1, p2, size):
        super().__init__(timeout=300)
        self.players = [p1, p2]
        self.turn = 0
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]

        for x in range(size):
            for y in range(size):
                self.add_item(CaroButton(x, y))

    def current_player(self):
        return self.players[self.turn]

# ===== COMMAND =====
@bot.command()
async def caro(ctx, opponent: discord.Member, size: int = 5):
    if size not in [5, 10]:
        return await ctx.send("Chỉ hỗ trợ 5 hoặc 10")

    view = CaroView(ctx.author, opponent, size)

    await ctx.send(
        f"🎮 Caro {size}x{size}\nLượt: {ctx.author.mention}",
        view=view
    )

bot.run(os.getenv("TOKEN"))