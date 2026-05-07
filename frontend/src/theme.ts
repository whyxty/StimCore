// Дизайн-токены StimCore (взяты из StimCore App.html)

export const T = {
  bg0:     '#04060a',
  bg1:     '#0a0d13',
  bg2:     '#131720',
  bg3:     '#1a1e28',
  border:  '#222a38',
  border2: '#2a3448',
  text0:   '#eef0f4',
  text1:   '#8a96a8',
  text2:   '#4a5568',
  text3:   '#2a3344',
  green:   '#7fff6e',
  orange:  '#ffb74d',
  red:     '#ff5555',
  purple:  '#a78bfa',
  accent:  '#00e5ff',
  mono:    "'JetBrains Mono', monospace",
  sans:    "'Inter', sans-serif",
} as const;

export type Theme = typeof T;
