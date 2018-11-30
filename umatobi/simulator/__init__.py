__doc__ = '''\
watson, client, darkness が主要な process。

watson:
    watson is process.
    Homes の良き partner である watson は，
    client からの依頼を待つ。
    simulation 毎に一つ必要となる process。
    simulation に関する全ての情報を握る。
client:
    client is Process.
    simulation に参加するPC毎に client を一つ作成する。
    client は，D 個の darkness process を作成する。
darkness:
    darkness is Process.
    client が複数起動する process が darkness。
    darkness は，N // D 個の node thread を作成する。
node:
    node is Thread.
    漆黒の闇の中で蠢く謎の node の姿が！
    なんだかんだで，localhost PC では，
    N 個の thread を simulation のために起動する。

.............................
process-thread 関係図

process-thread 関係図 では，
C 台のPCでのsimulationを想定。
C 個の client を抱える。
D 個の darkness を抱える。
N 個の nodes でのsimulationを想定。

Process means [P].
Thread means [T].

localhost PC

watson[P]-+-client.1[P]
          |   |
          |   +-darkness.1[P]
          |   | +-node.1[T]
          |   | +-node.2[T]
          |   | +-...
          |   | +-node.X[T]
          |   |
          |   +-darkness.2[P]
          |   | +-node.X+1[T]
          |   | +-node.X+2[T]
          |   | +-...
          |   | +-node.Y[T]
          |   |
          |   +-darkness.D[P]
          |     +-node.Y+1[T]
          |     +-node.Y+2[T]
          |     +-...
          |     +-node.N[T]
.............................
another   +-client.C[P]
PC        |   |
          |   +-darkness.D[P]
          |     +-node.N+1[T]
          |     +-...
          |     +-node.N[T]
.............................
another   |
PC        +-client.C+1[P]
              |
              +-darkness.D+1[P]
                +-node.N+1[T]
                +-...
別PCでも simulation に参加できる事を想定している。
'''
