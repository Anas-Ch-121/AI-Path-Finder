import tkinter as tk
import collections
import heapq
import time

GRID = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

MOVES = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1)]
COLORS = {0: "white", 1: "black", 'S': "green", 'T': "red",
          'F': "blue", 'E': "yellow", 'P': "purple"}

class Pathfinder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Search Visualizer")
        self.S = (8, 1)
        self.T = (2, 7)
        self.running = False
        self.rects = {}
        self.fast_mode = False
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.RIGHT, padx=20)
        for algo in ["BFS", "DFS", "UCS", "DLS", "IDDFS", "Bi-Dir"]:
            tk.Button(btn_frame, text=algo,
                      command=lambda a=algo: self.run(a)).pack(fill=tk.X)
        tk.Button(btn_frame, text="RESET", command=self.full_reset,
                  bg="red", fg="white").pack(fill=tk.X, pady=10)

        self.full_reset()

    def full_reset(self):
        self.running = False
        self.canvas.delete("all")
        for r in range(10):
            for c in range(10):
                color = COLORS[1] if GRID[r][c] else COLORS[0]
                if (r, c) == self.S:
                    color = COLORS['S']
                if (r, c) == self.T:
                    color = COLORS['T']
                self.rects[(r, c)] = self.canvas.create_rectangle(
                    c*40, r*40, (c+1)*40, (r+1)*40,
                    fill=color, outline="gray")
        self.update()

    def clear_search(self):
        """Lightweight reset for IDDFS (keeps start/goal/walls)."""
        self.running = False
        for n in self.rects:
            if n != self.S and n != self.T and GRID[n[0]][n[1]] == 0:
                self.canvas.itemconfig(self.rects[n], fill=COLORS[0])
        self.update()

    def color(self, n, c):
        """Color a cell if not start/goal. Sleep shorter in fast mode."""
        if self.running and n not in (self.S, self.T):
            self.canvas.itemconfig(self.rects[n], fill=COLORS[c])
            self.update()
            if c != 'P':
               
                time.sleep(0.002 if self.fast_mode else 0.02)

    def neighbors(self, r, c):
        """Yield ((nr,nc), cost) for all valid moves."""
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 10 and 0 <= nc < 10 and GRID[nr][nc] == 0:
               
                cost = 1.4 if dr != 0 and dc != 0 else 1.0
                yield (nr, nc), cost

    def run(self, algo):
        self.full_reset()
        self.running = True
        path = None

        if algo == "BFS":
            path = self.bfs()
        elif algo == "DFS":
            path = self.dfs()
        elif algo == "UCS":
            path = self.ucs()
        elif algo == "DLS":
            path = self.dls(15)
        elif algo == "IDDFS":
            
            self.fast_mode = True
            for depth in range(1, 50):
                if not self.running:
                    break
                self.clear_search()
                self.running = True
                path = self.dls(depth)
                if path:
                    break
            self.fast_mode = False
        elif algo == "Bi-Dir":
            path = self.bidirectional()

        if path:
            self.running = False
            for n in path:
                if n not in (self.S, self.T):
                    self.canvas.itemconfig(self.rects[n], fill=COLORS['P'])

    def backtrack(self, parent, curr):
        """Reconstruct path from parent dictionary."""
        path = []
        while curr:
            path.append(curr)
            curr = parent.get(curr)
        return path[::-1]

    def bfs(self):
        q = collections.deque([self.S])
        parent = {self.S: None}
        while q and self.running:
            curr = q.popleft()
            if curr == self.T:
                return self.backtrack(parent, curr)
            self.color(curr, 'E')
            for n, _ in self.neighbors(*curr):
                if n not in parent:
                    parent[n] = curr
                    q.append(n)
                    self.color(n, 'F')
        return None

    def dfs(self):
        stack = [self.S]
        visited = set()
        parent = {}
        while stack and self.running:
            curr = stack.pop()
            if curr == self.T:
                return self.backtrack(parent, curr)
            if curr not in visited:
                visited.add(curr)
                self.color(curr, 'E')
                for n, _ in reversed(list(self.neighbors(*curr))):
                    if n not in visited:
                        parent[n] = curr
                        stack.append(n)
                        self.color(n, 'F')
        return None

    def ucs(self):
        pq = [(0, self.S)]
        costs = {self.S: 0}
        parent = {self.S: None}
        while pq and self.running:
            cost, curr = heapq.heappop(pq)
            if curr == self.T:
                return self.backtrack(parent, curr)
            self.color(curr, 'E')
            for n, w in self.neighbors(*curr):
                new_cost = cost + w
                if n not in costs or new_cost < costs[n]:
                    costs[n] = new_cost
                    parent[n] = curr
                    heapq.heappush(pq, (new_cost, n))
                    self.color(n, 'F')
        return None

    def dls(self, limit):
        """Depth‑limited search (used by IDDFS)."""
        stack = [(self.S, 0, None)]
        parent = {}      
        visited = {}         

        while stack and self.running:
            curr, depth, par = stack.pop()
            if curr == self.T:
                parent[curr] = par
                return self.backtrack(parent, curr)
            if depth >= limit:
                continue
            # only process if not visited at a shallower depth
            if curr in visited and visited[curr] <= depth:
                continue
            visited[curr] = depth
            parent[curr] = par          # store correct parent for this occurrence
            self.color(curr, 'E')
            for n, _ in reversed(list(self.neighbors(*curr))):
                if n not in visited or visited[n] > depth + 1:
                    stack.append((n, depth + 1, curr))
                    self.color(n, 'F')
        return None

    def bidirectional(self):
        qF = collections.deque([self.S])
        qB = collections.deque([self.T])
        pF = {self.S: None}
        pB = {self.T: None}

        while qF and qB and self.running:
            if self._expand(qF, pF, pB):
                return self._merge(pF, pB, forward=True)
            if self._expand(qB, pB, pF):
                return self._merge(pB, pF, forward=False)
        return None

    def _expand(self, q, own_parent, other_parent):
        curr = q.popleft()
        self.color(curr, 'E')
        if curr in other_parent:
            self.meet = curr
            return True
        for n, _ in self.neighbors(*curr):
            if n not in own_parent:
                own_parent[n] = curr
                q.append(n)
                self.color(n, 'F')
        return False

    def _merge(self, p1, p2, forward):
        path1 = self.backtrack(p1, self.meet)
        path2 = self.backtrack(p2, self.meet)
        if forward:
            return path1 + path2[::-1][1:]
        else:
            return path2 + path1[::-1][1:]

if __name__ == "__main__":
    app = Pathfinder()
    app.mainloop()
