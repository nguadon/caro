import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== LOGIC =====
EMPTY = "⬜"
X = "❌"
O = "⭕"

games = {}

def create_board(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def board_to_text(board):
    text = "   " + " ".join(str(i) for i in range(len(board))) + "\n"
    for i, row in enumerate(board):
        text += f"{i}  " + " ".join(row) + "\n"
    return text

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

# ===== SYNC COMMAND =====
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ===== SLASH COMMAND =====
@bot.tree.command(name="caro", description="Chơi cờ caro")
@app_commands.describe(opponent="Người chơi cùng", size="Kích thước bàn (5 hoặc 10)")
async def caro(interaction: discord.Interaction, opponent: discord.Member, size: int):
    
    if size not in [5, 10]:
        return await interaction.response.send_message("Chỉ hỗ trợ 5 hoặc 10", ephemeral=True)

    board = create_board(size)

    games[interaction.channel.id] = {
        "board": board,
        "players": [interaction.user, opponent],
        "turn": 0
    }

    await interaction.response.send_message(
        f"🎮 Caro {size}x{size}\n```{board_to_text(board)}```\nLượt: {interaction.user.mention}"
    )

# ===== ĐÁNH =====
@bot.tree.command(name="danh", description="Đánh cờ")
@app_commands.describe(x="Hàng", y="Cột")
async def danh(interaction: discord.Interaction, x: int, y: int):
    
    game = games.get(interaction.channel.id)
    if not game:
        return await interaction.response.send_message("Chưa có game", ephemeral=True)

    player = game["players"][game["turn"]]
    if interaction.user != player:
        return await interaction.response.send_message("Không phải lượt bạn", ephemeral=True)

    board = game["board"]

    if not (0 <= x < len(board) and 0 <= y < len(board)):
        return await interaction.response.send_message("Tọa độ không hợp lệ", ephemeral=True)

    if board[x][y] != EMPTY:
        return await interaction.response.send_message("Ô đã đánh", ephemeral=True)

    symbol = X if game["turn"] == 0 else O
    board[x][y] = symbol

    if check_win(board, x, y, symbol):
        del games[interaction.channel.id]
        return await interaction.response.send_message(
            f"```{board_to_text(board)}```\n🏆 {interaction.user.mention} thắng!"
        )

    game["turn"] = 1 - game["turn"]

    await interaction.response.send_message(
        f"```{board_to_text(board)}```\nLượt: {game['players'][game['turn']].mention}"
    )

bot.run(os.getenv("TOKEN"))