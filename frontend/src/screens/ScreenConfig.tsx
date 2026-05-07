import { useEffect, useState } from 'react';
import { T } from '../theme';
import { Card, CardHeader, Field, Tag } from '../components/atoms';
import { fetchDefaultConfig } from '../api';

type Cfg = Record<string, unknown>;

export function ScreenConfig() {
  const [cfg, setCfg] = useState<Cfg | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchDefaultConfig().then(setCfg).catch(e => setErr(String(e)));
  }, []);

  if (err) return <Centered>{err}</Centered>;
  if (!cfg) return <Centered>Загрузка профиля…</Centered>;

  const fieldName = (cfg.field_name as string) || '—';

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <Heading
        title="Настройки месторождения"
        subtitle={`Профиль: ${fieldName}`}
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <SectionCfg title="Критерии отбора скважины" group={cfg.well_selection as Cfg} />
        <SectionCfg title="Реакционная кинетика"     group={cfg.reaction_kinetics as Cfg} />
        <SectionCfg title="Свойства породы"          group={cfg.rock_properties as Cfg} />
        <SectionCfg title="Коэффициенты растворения" group={cfg.dissolution_coefficients as Cfg} />
        <SectionCfg title="Изм. пр-сти после СКО"    group={cfg.permeability_change_after_sko as Cfg} />
      </div>

      <Card>
        <CardHeader title="Регрессии k₀ = A·m₀^B (табл. В.11)" accent={T.accent} />
        <div style={{ padding: 14 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.mono, fontSize: 11 }}>
            <thead>
              <tr style={{ color: T.text2 }}>
                <th style={th}>КЛ</th>
                <th style={th}>Тип</th>
                <th style={{ ...th, textAlign: 'right' }}>A</th>
                <th style={{ ...th, textAlign: 'right' }}>B</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(cfg.permeability_regressions as Cfg).filter(([k]) => k.startsWith('KL_'))
                .map(([k, v]) => {
                  const ct = (cfg.collector_types as Cfg)?.[k] as Cfg | undefined;
                  return (
                    <tr key={k} style={{ color: T.text0, borderTop: `1px solid ${T.border}` }}>
                      <td style={td}>{k.replace('KL_', '')}</td>
                      <td style={td}>{(ct?.name as string) || '—'}</td>
                      <td style={{ ...td, textAlign: 'right', color: T.accent }}>{(v as Cfg).A as number}</td>
                      <td style={{ ...td, textAlign: 'right', color: T.accent }}>{(v as Cfg).B as number}</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </Card>

      <Card>
        <CardHeader title="Удельные дебиты по пористости (табл. В.2)" accent={T.green} />
        <div style={{ padding: 14, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {((cfg.specific_debit_table as Cfg)?.rows as Cfg[] || []).map((r, i) => (
            <div key={i} style={{
              border: `1px solid ${T.border}`, borderRadius: 6, padding: '8px 12px',
              background: T.bg1, fontFamily: T.mono, fontSize: 11, color: T.text1,
            }}>
              <span style={{ color: T.text2 }}>m₀ = </span>
              <span style={{ color: T.text0 }}>
                {(r.porosity_min as number)}–{(r.porosity_max as number) < 999 ? r.porosity_max as number : '∞'}%
              </span>
              <span style={{ color: T.text3 }}> → q_уд = </span>
              <span style={{ color: T.green, fontWeight: 700 }}>{r.specific_debit as number}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function SectionCfg({ title, group }: { title: string; group: Cfg | undefined }) {
  if (!group) return null;
  return (
    <Card>
      <CardHeader title={title} accent={T.accent} />
      <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {Object.entries(group)
          .filter(([k, v]) => !k.startsWith('comment') && typeof v !== 'object')
          .map(([k, v]) => (
            <Field
              key={k}
              label={k}
              value={String(v)}
              accent={T.accent}
            />
          ))}
      </div>
    </Card>
  );
}

function Heading({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <Tag>STIMCORE · CONFIG</Tag>
      <div style={{ fontSize: 22, fontWeight: 700, color: T.text0, letterSpacing: '-0.02em', marginTop: 4 }}>
        {title}
      </div>
      <div style={{ fontFamily: T.mono, fontSize: 11, color: T.text2, marginTop: 4 }}>
        {subtitle}
      </div>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: T.text2, fontFamily: T.mono,
    }}>{children}</div>
  );
}

const th: React.CSSProperties = {
  padding: '6px 8px', textAlign: 'left',
  fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
};
const td: React.CSSProperties = { padding: '6px 8px' };
