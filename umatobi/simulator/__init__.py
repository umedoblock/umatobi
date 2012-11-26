__doc__ = '''\
watson, client, darkness が主要な process。
watson: client からの依頼を待つ。
      : simulation 毎に一つ必要となる process。
client: 多くの darkness を抱える。
      : simulation に参加するPC毎に一つ作成する。
darkness: 漆黒の闇の中で蠢く謎の node の姿が！
        : client が起動する process。

process 関係図

watson-+-client.1
       |  |
       |  +-darkness.1
       |  | +-node.1
       |  | +-node.?
       |  | +-node.381
       |  |
       |  +-darkness.X
       |  | +-node.X
       |  |
       |  +-darkness.31
       |    +-node.7936
       |    +-node.?
       |    +-node.8139
       |
       +-client.?'''
