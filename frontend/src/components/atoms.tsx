// Базовые UI-атомы (взяты из StimCore App.html)
import type { ReactNode, CSSProperties } from 'react';
import { T } from '../theme';

export const Badge = ({ children, color }: { children: ReactNode; color: string }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', padding: '2px 7px',
    borderRadius: 3, background: color + '18', border: `1px solid ${color}33`,
    color, fontFamily: T.mono, fontSize: 9, fontWeight: 700,
    letterSpacing: '0.1em', textTransform: 'uppercase', whiteSpace: 'nowrap'
  }}>{children}</span>
);

export const Dot = ({ color, size = 6, pulse = false }: { color: string; size?: number; pulse?: boolean }) => (
  <span style={{
    display: 'inline-block', width: size, height: size, borderRadius: '50%',
    background: color, boxShadow: `0 0 ${size}px ${color}`, flexShrink: 0,
    animation: pulse ? 'stimPulse 2s ease-in-out infinite' : 'none',
    ['--accent' as string]: color,
  } as CSSProperties} />
);

export const Tag = ({ children }: { children: ReactNode }) => (
  <span style={{
    fontFamily: T.mono, fontSize: 9, fontWeight: 700,
    letterSpacing: '0.16em', textTransform: 'uppercase', color: T.text3,
  }}>{children}</span>
);

export const Divider = () => <div style={{ height: 1, background: T.border, margin: '12px 0' }} />;

export const Stat = ({
  label, value, unit, color, large = false,
}: { label: string; value: ReactNode; unit?: string; color: string; large?: boolean }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
    <Tag>{label}</Tag>
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
      <span style={{
        fontFamily: T.mono, fontSize: large ? 28 : 18, fontWeight: 700,
        color, letterSpacing: '-0.02em', lineHeight: 1
      }}>{value}</span>
      {unit && <span style={{ fontSize: 10, color: T.text2, fontFamily: T.mono }}>{unit}</span>}
    </div>
  </div>
);

export const Card = ({
  children, style = {}, glow,
}: { children: ReactNode; style?: CSSProperties; glow?: string }) => (
  <div style={{
    background: T.bg2, borderRadius: 8,
    border: `1px solid ${glow ? glow + '33' : T.border}`,
    boxShadow: glow ? `0 0 20px ${glow}0a` : 'none',
    ...style,
  }}>{children}</div>
);

export const CardHeader = ({
  title, right, accent,
}: { title: string; right?: ReactNode; accent: string }) => (
  <div style={{
    padding: '10px 14px', borderBottom: `1px solid ${T.border}`,
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
      <Dot color={accent} size={5} />
      <span style={{
        fontFamily: T.mono, fontSize: 9, fontWeight: 700,
        letterSpacing: '0.14em', textTransform: 'uppercase', color: T.text2,
      }}>{title}</span>
    </div>
    {right && <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>{right}</div>}
  </div>
);

export const Field = ({
  label, value, unit, onChange, accent,
}: {
  label: string;
  value: string | number;
  unit?: string;
  onChange?: (v: string) => void;
  accent: string;
}) => (
  <div style={{
    display: 'grid', gridTemplateColumns: '1fr 96px 44px',
    alignItems: 'center', gap: 6,
  }}>
    <span style={{
      fontFamily: T.mono, fontSize: 10, color: T.text2, lineHeight: 1.3,
      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
    }}>{label}</span>
    <input
      defaultValue={value}
      onChange={e => onChange?.(e.target.value)}
      style={{
        width: '100%', background: T.bg0,
        border: `1px solid ${T.border2}`, borderRadius: 4,
        padding: '5px 8px', color: accent,
        fontFamily: T.mono, fontSize: 12, fontWeight: 600,
        outline: 'none', textAlign: 'right',
        transition: 'border-color .15s',
      }}
      onFocus={e => (e.target.style.borderColor = accent + '88')}
      onBlur={e => (e.target.style.borderColor = T.border2)}
    />
    <span style={{
      fontSize: 10, color: T.text3, fontFamily: T.mono,
      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
    }}>{unit || ''}</span>
  </div>
);

export const Button = ({
  children, onClick, primary = false, disabled = false,
}: {
  children: ReactNode; onClick?: () => void; primary?: boolean; disabled?: boolean;
}) => (
  <button
    onClick={onClick}
    disabled={disabled}
    style={{
      background: primary ? T.accent : T.bg2,
      color: primary ? T.bg0 : T.text1,
      border: primary ? 'none' : `1px solid ${T.border2}`,
      borderRadius: 6, padding: '8px 18px',
      fontFamily: T.mono, fontSize: 11, fontWeight: 700,
      letterSpacing: '0.1em', textTransform: 'uppercase',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      boxShadow: primary ? `0 0 18px ${T.accent}44` : 'none',
      transition: 'all .15s',
    }}
  >{children}</button>
);
