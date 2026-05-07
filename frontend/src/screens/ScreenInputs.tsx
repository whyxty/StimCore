import { T } from '../theme';
import { Card, CardHeader, Field, Tag, Badge, Button } from '../components/atoms';
import type { Inputs } from '../store';

interface Props {
  inputs: Inputs;
  setInputs: React.Dispatch<React.SetStateAction<Inputs>>;
  onCalculate: () => void;
  loading: boolean;
}

type FieldDef = { key: keyof Inputs; label: string; unit?: string };

const SECTIONS: { title: string; fields: FieldDef[] }[] = [
  {
    title: 'Идентификация и общие параметры',
    fields: [
      { key: 'well_name',  label: 'Название скважины' },
      { key: 'H',          label: 'Глубина пласта H',                  unit: 'м' },
      { key: 'r_c',        label: 'Радиус скважины r_c',               unit: 'м' },
      { key: 'h_ef',       label: 'Эфф. толщина h_эф',                 unit: 'м' },
      { key: 'm0',         label: 'Пористость m₀',                     unit: '%' },
      { key: 'p_pl',       label: 'Пластовое давление p_пл',           unit: 'МПа' },
      { key: 'T_pl',       label: 'Пластовая температура T_пл',        unit: '°C' },
      { key: 'r_k',        label: 'Радиус контура питания r_к',        unit: 'м' },
    ],
  },
  {
    title: 'Продуктивность и приёмистость',
    fields: [
      { key: 'K_f',        label: 'K_ф (фактич.)',                      unit: 'т/(сут·МПа)' },
      { key: 'K_pot',      label: 'K_пот (потенц.)',                    unit: 'т/(сут·МПа)' },
      { key: 'Q_f',        label: 'Q_ф фактич. дебит',                  unit: 'м³/сут' },
      { key: 'q_inj',      label: 'q приёмистость',                     unit: 'м³/сут' },
      { key: 'h_pta',      label: 'h_пгл поглощ. толщина',              unit: 'м' },
      { key: 'W_0',        label: 'Обводнённость W₀',                   unit: '%' },
      { key: 'rho_n',      label: 'Плотность нефти ρ_н',                unit: 'кг/м³' },
    ],
  },
  {
    title: 'Состав породы и коэффициенты',
    fields: [
      { key: 'C_k',        label: 'Карбонатность C_к',                  unit: '%' },
      { key: 'C_gl',       label: 'Глинистость C_гл',                   unit: '%' },
      { key: 'rho_p',      label: 'Плотность пористой ρ_п',             unit: 'кг/м³' },
      { key: 'rho_sk',     label: 'Плотность скелета ρ_ск',             unit: 'кг/м³' },
      { key: 'k_vo',       label: 'k_в.о (охват по верт.)',             unit: '' },
      { key: 'k_uf',       label: 'k_у.ф (участие пор)',                unit: '' },
      { key: 'k_v',        label: 'k_в (вытеснение)',                   unit: '' },
      { key: 'k_ms_lab',   label: 'k_ms (СКО, лаб.)',                   unit: '' },
      { key: 'k_mg_lab',   label: 'k_mg (ГКО, лаб.)',                   unit: '' },
    ],
  },
  {
    title: 'Параметры закачки СКР',
    fields: [
      { key: 'C0_HCl',     label: 'C₀ HCl (концентрация)',              unit: '%' },
      { key: 'q_k',        label: 'q_к расход СКР',                     unit: 'м³/сут' },
      { key: 'V_zad',      label: 'V_ks (заданный)',                    unit: 'м³' },
      { key: 'p_opr',      label: 'p_опр опрессовки',                   unit: 'МПа' },
      { key: 'p_k',        label: 'p_к на устье',                       unit: 'МПа' },
      { key: 'rho_fluid',  label: 'ρ жидкости',                          unit: 'кг/м³' },
      { key: 'R_ms',       label: 'R_ms растворимость',                 unit: 'кг/(м³·экв)' },
    ],
  },
  {
    title: 'Конструкция скважины (для В.10)',
    fields: [
      { key: 'd_in_NKT',   label: 'd_вн НКТ',                           unit: 'м' },
      { key: 'd_out_NKT',  label: 'd_нар НКТ',                          unit: 'м' },
      { key: 'D_k',        label: 'D_к экспл. колонны',                 unit: 'м' },
      { key: 'H_no',       label: 'H_н.о ниж. отверстие',                unit: 'м' },
      { key: 'H_vo',       label: 'H_в.о верх. отверстие',               unit: 'м' },
    ],
  },
  {
    title: 'Состав нефти и пласт. вод (для В.11)',
    fields: [
      { key: 'N_as',       label: 'N_ас асфальтены',                    unit: '%' },
      { key: 'N_sm',       label: 'N_см смолы',                          unit: '%' },
      { key: 'N_nf',       label: 'N_нф нафтеновые кислоты',             unit: '%' },
      { key: 'Fe3',        label: 'Fe³⁺ ожидаемое',                      unit: '%' },
      { key: 'N_ko',       label: 'N_ко прошлых обработок',              unit: 'шт' },
      { key: 'HCl',        label: 'HCl в КР',                            unit: '%' },
      { key: 'HF',         label: 'HF (если ГКО)',                       unit: '%' },
    ],
  },
  {
    title: 'Эффективность и экономика (для В.9)',
    fields: [
      { key: 'T_n',        label: 'T_н длит. эффекта',                   unit: 'сут' },
      { key: 'C_n',        label: 'Ц_н цена нефти',                      unit: 'руб/т' },
      { key: 'S_n',        label: 'С_н себестоимость',                   unit: 'руб/т' },
      { key: 'Z_ko',       label: 'Z_к.о стоимость СКО',                 unit: 'руб' },
    ],
  },
  {
    title: 'Концентрации добавок (для В.17)',
    fields: [
      { key: 'C_inh',      label: 'C ингибитора',                        unit: '%' },
      { key: 'C_stab',     label: 'C стабилизатора',                     unit: '%' },
      { key: 'C_surf',     label: 'C ПАВ в КР',                          unit: '%' },
      { key: 'C_buf',      label: 'C ПАВ в буферах',                     unit: '%' },
    ],
  },
];

export function ScreenInputs({ inputs, setInputs, onCalculate, loading }: Props) {
  const update = (key: keyof Inputs, raw: string) => {
    setInputs(prev => {
      const cur = prev[key] as unknown;
      let v: unknown = raw;
      if (typeof cur === 'number') {
        const n = parseFloat(raw.replace(',', '.'));
        v = Number.isFinite(n) ? n : cur;
      } else if (typeof cur === 'boolean') {
        v = raw === 'true';
      }
      return { ...prev, [key]: v };
    });
  };

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div>
          <Tag>STIMCORE · INPUTS</Tag>
          <div style={{ fontSize: 22, fontWeight: 700, color: T.text0, letterSpacing: '-0.02em', marginTop: 4 }}>
            Исходные данные скважины
          </div>
          <div style={{ fontFamily: T.mono, fontSize: 11, color: T.text2, marginTop: 4 }}>
            Заполните параметры. Все 12 задач рассчитываются за один проход.
          </div>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Badge color={T.orange}>не сохранено</Badge>
          <Button primary onClick={onCalculate} disabled={loading}>
            {loading ? 'считаем…' : 'посчитать ⏎'}
          </Button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {SECTIONS.map(s => (
          <Card key={s.title}>
            <CardHeader title={s.title} accent={T.accent} />
            <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
              {s.fields.map(f => (
                <Field
                  key={f.key as string}
                  label={f.label}
                  value={String(inputs[f.key])}
                  unit={f.unit}
                  accent={T.accent}
                  onChange={v => update(f.key, v)}
                />
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
