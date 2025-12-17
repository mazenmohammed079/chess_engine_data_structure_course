#include <iostream>
#include <vector>
#include <string>
#include <cctype>
#include <cmath>
#include <unordered_map>
#include <stack>

using namespace std;

// ================= ENUMS =================
enum PieceType { EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING };
enum Color { NONE, WHITE, BLACK };

// ================= PIECE =================
struct Piece {
    PieceType type;
    Color color;
    bool hasMoved;
    Piece() : type(EMPTY), color(NONE), hasMoved(false) {}
    Piece(PieceType t, Color c) : type(t), color(c), hasMoved(false) {}
};

// ================= MOVE =================
struct Move {
    int fromRow, fromCol, toRow, toCol;
    PieceType promotion;
    bool isEnPassant, isCastling;
    Move() : promotion(EMPTY), isEnPassant(false), isCastling(false) {}
};

// ================ MOVE HISTORY NODE =================
struct MoveNode {
    Move move;
    MoveNode* prev;
    MoveNode* next;
    MoveNode(const Move& m) : move(m), prev(nullptr), next(nullptr) {}
};

// ================= GAME =================
class ChessGame {
private:
    Piece board[8][8];
    Color currentPlayer;
    int enPassantCol, enPassantRow;
    int halfMoveClock;
    unordered_map<string,int> positionCount;

    struct GameState {
        Piece board[8][8];
        Color currentPlayer;
        int enPassantCol, enPassantRow;
        int halfMoveClock;
        unordered_map<string,int> positionCount;
    };

    stack<GameState> undoStack;
    stack<GameState> redoStack;

    MoveNode* historyHead;
    MoveNode* historyTail;
    MoveNode* historyCurrent;

public:
    ChessGame() {
        currentPlayer = WHITE;
        enPassantCol = enPassantRow = -1;
        halfMoveClock = 0;
        historyHead = historyTail = historyCurrent = nullptr;
        setupBoard();
        positionCount[getPositionKey()]++;
    }

    ~ChessGame() {
        MoveNode* n = historyHead;
        while (n) {
            MoveNode* next = n->next;
            delete n;
            n = next;
        }
    }

    // ---------- SETUP ----------
    void setupBoard() {
        for (auto& r : board)
            for (auto& c : r)
                c = Piece();

        PieceType back[] = {ROOK,KNIGHT,BISHOP,QUEEN,KING,BISHOP,KNIGHT,ROOK};
        for (int i = 0; i < 8; i++) {
            board[0][i] = Piece(back[i], BLACK);
            board[1][i] = Piece(PAWN, BLACK);
            board[6][i] = Piece(PAWN, WHITE);
            board[7][i] = Piece(back[i], WHITE);
        }
    }

    // ---------- HELPERS ----------
    char getPieceChar(Piece p) {
        if (p.type == EMPTY) return '.';
        char map[] = {' ', 'P','N','B','R','Q','K'};
        char ch = map[p.type];
        return p.color == BLACK ? tolower(ch) : ch;
    }

    // displayBoard function was here

    Color opponent(Color c) { return c == WHITE ? BLACK : WHITE; }
    bool isValid(int r,int c) { return r>=0 && r<8 && c>=0 && c<8; }

    void findKing(Color c,int &kr,int &kc) {
        for (int r=0;r<8;r++)
            for (int c2=0;c2<8;c2++)
                if (board[r][c2].type==KING && board[r][c2].color==c) {
                    kr=r; kc=c2; return;
                }
    }

    // ---------- STATE SNAPSHOT ----------
    GameState getState() {
        GameState s;
        for (int r = 0; r < 8; ++r)
            for (int c = 0; c < 8; ++c)
                s.board[r][c] = board[r][c];
        s.currentPlayer = currentPlayer;
        s.enPassantCol = enPassantCol;
        s.enPassantRow = enPassantRow;
        s.halfMoveClock = halfMoveClock;
        s.positionCount = positionCount;
        return s;
    }

    void setState(const GameState& s) {
        for (int r = 0; r < 8; ++r)
            for (int c = 0; c < 8; ++c)
                board[r][c] = s.board[r][c];
        currentPlayer = s.currentPlayer;
        enPassantCol = s.enPassantCol;
        enPassantRow = s.enPassantRow;
        halfMoveClock = s.halfMoveClock;
        positionCount = s.positionCount;
    }

    // ---------- MOVE HISTORY ----------

    // truncateHistoryAfterCurrent function was here

    void addMoveToHistory(const Move& m) {
        MoveNode* node=new MoveNode(m);
        if (!historyHead) {
            historyHead=historyTail=historyCurrent=node;
        } else {
            node->prev=historyTail;
            historyTail->next=node;
            historyTail=node;
            historyCurrent=node;
        }
    }

    // moveToString and printMoveHistoryReport functions were here

    // ---------- ATTACK CHECK ----------
    bool isSquareAttacked(int tr,int tc,Color by) {
        for (int r=0;r<8;r++)
            for (int c=0;c<8;c++) {
                Piece p=board[r][c];
                if (p.color!=by) continue;

                if (p.type==PAWN) {
                    int dir=(by==WHITE?-1:1);
                    if (r+dir==tr && abs(c-tc)==1) return true;
                }
                else if (canPieceMoveTo(r,c,tr,tc,true))
                    return true;
            }
        return false;
    }

    bool isInCheck(Color c) {
        int kr,kc;
        findKing(c,kr,kc);
        return isSquareAttacked(kr,kc,opponent(c));
    }

    // ---------- MOVE LOGIC ----------
    bool canPieceMoveTo(int fr,int fc,int tr,int tc,bool ignoreCheck) {
        Piece p=board[fr][fc];
        if (p.type==EMPTY || board[tr][tc].color==p.color) return false;

        int dr=tr-fr, dc=tc-fc;

        if (p.type==PAWN) {
            int dir=(p.color==WHITE?-1:1);
            if (dc==0 && dr==dir && board[tr][tc].type==EMPTY) return true;
            if (dc==0 && dr==2*dir && !p.hasMoved &&
                board[fr+dir][fc].type==EMPTY &&
                board[tr][tc].type==EMPTY) return true;
            if (abs(dc)==1 && dr==dir) {
                if (board[tr][tc].type!=EMPTY) return true;
                if (tc==enPassantCol &&
                    tr==(p.color==WHITE?2:5)) return true;
            }
            return false;
        }

        if (p.type==KNIGHT)
            return (abs(dr)==2 && abs(dc)==1)||(abs(dr)==1 && abs(dc)==2);

        if (p.type==KING) {
            if (abs(dr)<=1 && abs(dc)<=1) return true;
            if (!ignoreCheck && dr==0 && abs(dc)==2 && !p.hasMoved) {
                int rookCol = dc>0?7:0;
                int step = dc>0?1:-1;
                if (board[fr][rookCol].type==ROOK &&
                    !board[fr][rookCol].hasMoved) {
                    for (int c=fc+step;c!=rookCol;c+=step)
                        if (board[fr][c].type!=EMPTY) return false;
                    if (!isSquareAttacked(fr,fc,opponent(p.color)) &&
                        !isSquareAttacked(fr,fc+step,opponent(p.color)) &&
                        !isSquareAttacked(tr,tc,opponent(p.color)))
                        return true;
                }
            }
            return false;
        }

        bool diag=abs(dr)==abs(dc);
        bool straight=dr==0||dc==0;
        if (p.type==BISHOP && !diag) return false;
        if (p.type==ROOK && !straight) return false;
        if (p.type==QUEEN && !(diag||straight)) return false;

        int sr=(dr>0)-(dr<0), sc=(dc>0)-(dc<0);
        for (int r=fr+sr,c=fc+sc;r!=tr||c!=tc;r+=sr,c+=sc)
            if (board[r][c].type!=EMPTY) return false;

        return true;
    }

    bool testMove(int fr,int fc,int tr,int tc) {
        Piece a=board[fr][fc], b=board[tr][tc];
        board[tr][tc]=a; board[fr][fc]=Piece();
        bool ok=!isInCheck(a.color);
        board[fr][fc]=a; board[tr][tc]=b;
        return ok;
    }

    vector<Move> getLegalMoves(Color c) {
        vector<Move> moves;
        for (int r=0;r<8;r++)
            for (int col=0;col<8;col++)
                if (board[r][col].color==c)
                    for (int tr=0;tr<8;tr++)
                        for (int tc=0;tc<8;tc++)
                            if (canPieceMoveTo(r,col,tr,tc,false) &&
                                testMove(r,col,tr,tc)) {
                                Move m;
                                m.fromRow=r; m.fromCol=col;
                                m.toRow=tr;  m.toCol=tc;
                                if (board[r][col].type==KING && abs(tc-col)==2)
                                    m.isCastling=true;
                                if (board[r][col].type==PAWN &&
                                    tc==enPassantCol &&
                                    tr==(c==WHITE?2:5))
                                    m.isEnPassant=true;
                                if (board[r][col].type==PAWN &&
                                   (tr==0||tr==7)) {
                                    PieceType ps[]={QUEEN,ROOK,BISHOP,KNIGHT};
                                    for (auto p:ps){Move pm=m;pm.promotion=p;moves.push_back(pm);}
                                } else moves.push_back(m);
                            }
        return moves;
    }

    // ---------- STATUS ----------
    string getPositionKey() {
        string k;
        for (int r=0;r<8;r++)
            for (int c=0;c<8;c++){
                k+=char('0'+board[r][c].type);
                k+=char('0'+board[r][c].color);
            }
        k+=char('0'+currentPlayer);
        return k;
    }

    bool insufficientMaterial() {
        int minor=0;
        for (auto&r:board)for(auto&p:r)
            if (p.type!=EMPTY && p.type!=KING) {
                if (p.type==BISHOP||p.type==KNIGHT) minor++;
                else return false;
            }
        return minor<=1;
    }

    string getGameStatus() {
        if (positionCount[getPositionKey()]>=3) return "draw (threefold repetition)";
        if (halfMoveClock>=100) return "draw (50-move rule)";
        if (insufficientMaterial()) return "draw (insufficient material)";

        auto moves=getLegalMoves(currentPlayer);
        if (moves.empty())
            return isInCheck(currentPlayer)?"checkmate":"stalemate";
        if (isInCheck(currentPlayer)) return "check";
        return "active";
    }


    // ---------- MAKE MOVE ----------
    void makeMove(Move m) {
    undoStack.push(getState());
    while (!redoStack.empty()) redoStack.pop();
    addMoveToHistory(m);

    Piece p=board[m.fromRow][m.fromCol];
    if (p.type==PAWN || board[m.toRow][m.toCol].type!=EMPTY)
        halfMoveClock=0;
    else halfMoveClock++;

    // 🔥 FIX: En Passant - remove the captured pawn (it's NOT at the target square!)
    if (m.isEnPassant) {
        // The captured pawn is one row back from where we're moving
        int capturedPawnRow = (p.color == WHITE) ? m.toRow + 1 : m.toRow - 1;
        board[capturedPawnRow][m.toCol] = Piece();
    }

    // Update en passant tracking
    enPassantCol=enPassantRow=-1;
    if (p.type==PAWN && abs(m.toRow-m.fromRow)==2) {
        enPassantCol=m.toCol;
        enPassantRow=m.toRow;  // This is the target row for en passant capture
    }

    // Handle castling
    if (m.isCastling) {
        int rookFrom = m.toCol>m.fromCol?7:0;
        int rookTo   = m.toCol>m.fromCol?m.toCol-1:m.toCol+1;
        board[m.fromRow][rookTo]=board[m.fromRow][rookFrom];
        board[m.fromRow][rookFrom]=Piece();
    }

    // Move the piece
    board[m.toRow][m.toCol]=p;
    board[m.toRow][m.toCol].hasMoved=true;
    board[m.fromRow][m.fromCol]=Piece();

    // Handle promotion
    if (m.promotion!=EMPTY)
        board[m.toRow][m.toCol].type=m.promotion;

    currentPlayer=opponent(currentPlayer);
    positionCount[getPositionKey()]++;
}

    void undo() {
        if (undoStack.empty()) return;
        // Save current state to redo stack
        redoStack.push(getState());
        // Restore previous state
        GameState prev = undoStack.top();
        undoStack.pop();
        setState(prev);

        // Move historyCurrent one step back (if possible)
        if (historyCurrent) {
            historyCurrent = historyCurrent->prev;
        }
    }

    void redo() {
        if (redoStack.empty()) return;
        // Save current state to undo stack
        undoStack.push(getState());
        // Restore next state
        GameState next = redoStack.top();
        redoStack.pop();
        setState(next);

        // Move historyCurrent one step forward (if possible)
        if (!historyCurrent) {
            historyCurrent = historyHead;
        } else if (historyCurrent->next) {
            historyCurrent = historyCurrent->next;
        }
    }

    bool parseMove(string s,Move &m) {
        if (s.size()<4) return false;
        for(char &c:s)c=tolower(c);
        m.fromCol=s[0]-'a'; m.fromRow=8-(s[1]-'0');
        m.toCol=s[2]-'a';   m.toRow=8-(s[3]-'0');
        if (s.size()>=5) {
            char p=toupper(s[4]);
            if (p=='Q')m.promotion=QUEEN;
            if (p=='R')m.promotion=ROOK;
            if (p=='B')m.promotion=BISHOP;
            if (p=='N')m.promotion=KNIGHT;
        }
        return isValid(m.fromRow,m.fromCol)&&isValid(m.toRow,m.toCol);
    }

    // ---------- STREAMLIT-FRIENDLY OUTPUT ----------
    void printState() {
        cout << "BOARD\n";
        for (int r=0;r<8;r++) {
            for (int c=0;c<8;c++) {
                cout << getPieceChar(board[r][c]);
                if (c<7) cout<<" ";
            }
            cout<<"\n";
        }
        cout << "TURN " << (currentPlayer==WHITE?"WHITE":"BLACK") << "\n";
        cout << "STATUS " << getGameStatus() << "\n";
        cout << flush;
    }

    // ---------- COMMAND LOOP ----------
    void play() {
        printState();
        string cmd;
        while (cin >> cmd) {
            if (cmd=="QUIT") break;
            else if (cmd=="UNDO") undo();
            else if (cmd=="REDO") redo();
            else if (cmd=="MOVE") {
                string s; cin >> s;
                Move u,a;
                if (!parseMove(s,u)) {
                    cout<<"ERROR InvalidMove\n"<<flush;
                    printState();        // 🔥 ADD THIS, for a GUI ERROR
                    continue;
                }
                bool ok=false;
                for (auto m:getLegalMoves(currentPlayer))
                    if (m.fromRow==u.fromRow&&m.fromCol==u.fromCol&&
                        m.toRow==u.toRow&&m.toCol==u.toCol) {
                        a=m; ok=true; break;
                    }
                if (!ok) {
                    cout<<"ERROR IllegalMove\n"<<flush;
                    printState();        // 🔥 ADD THIS, for a GUI ERROR
                    continue;
                }
                makeMove(a);
            }
            printState();
        }
    }
};

// ================= MAIN =================
int main() {
    ChessGame game;
    game.play();
    return 0;
}