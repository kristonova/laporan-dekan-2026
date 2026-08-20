export type ChartValue = string | number | null | undefined;

export interface TableColumn<Row extends Record<string, unknown> = Record<string, unknown>> {
  key: keyof Row | string;
  label: string;
  align?: "start" | "center" | "end";
  format?: (value: unknown, row: Row) => string;
}

export interface ChartChromeProps<Row extends Record<string, unknown> = Record<string, unknown>> {
  id?: string;
  title: string;
  deck?: string;
  source?: string;
  extracted?: string;
  csvHref?: string;
  tableCaption?: string;
  tableRows?: Row[];
  tableColumns?: TableColumn<Row>[];
  class?: string;
  hideHeader?: boolean;
}

export interface ChartSeries {
  key: string;
  label: string;
  color?: string;
  pattern?: "solid" | "diagonal" | "dots" | "cross";
}

export type TckStatus = "tercapai" | "mendekati" | "tertinggal" | "meleset";
