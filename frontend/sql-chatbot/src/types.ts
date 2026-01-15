export interface ChatResponse {
  sql_query: string;
  result: any[][];
  explanation: string;
  row_count: number;
  model_used?: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type: 
    | 'text'
    | 'response'   
    | 'error';

  data?: {
    sql?: string;
    explanation?: string;
    tableData?: any[][];
    modelInfo?: string;
    rowCount?: number;   
    error?: string;
  };
}
