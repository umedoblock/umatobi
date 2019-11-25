# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

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

watson[P]-+-client.0[P]
          |   |
          |   +-darkness.0[P]
          |   | +-node.0[T]
          |   | +-node.1[T]
          |   | +-...
          |   | +-node.X-1[T]
          |   |
          |   +-darkness.1[P]
          |   | +-node.X[T]
          |   | +-node.X+1[T]
          |   | +-...
          |   | +-node.Y-1[T]
          |   |
          |   +-darkness.D-1[P]
          |     +-node.Y[T]
          |     +-node.Y+1[T]
          |     +-...
          |     +-node.N-1[T]
.............................
another   +-client.C+0[P]
PC        |   |
          |   +-darkness.D+0[P]
          |     +-node.N[T]
          |     +-...
          |     +-node.?[T]
.............................
another   |
PC2       +-client.C+1[P]
              |
              +-darkness.D+1[P]
                +-node.?[T]
                +-...
別PCでも simulation に参加できる事を想定している。
'''
