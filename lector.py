import pandas as pd
import os

def leer_excel_dinamico(archivo_excel):
    if not os.path.exists(archivo_excel):
        print(f"El archivo '{archivo_excel}' no existe.")
        return

    try:
        df = pd.read_excel(archivo_excel, header=None)
        
        for i, fila in df.iterrows():
            if 'ITEM NO.' in [str(v) for v in fila.values]:
                df.columns = df.iloc[i]
                df = df.iloc[i+1:].reset_index(drop=True)
                break
        else:
            return

        mapa = {
            'ITEM NO.': 'Item',
            'DESCRIPTION': 'Descripción',
            'QUANTTIY\n(UNIT)': 'Cantidad',
            'FOB QINGDAO\nUNIT PRICE\nPER UNIT': 'Precio Unit.',
            'TOTAL AMOUNT': 'Total'
        }
        
        columnas_finales = []
        nuevos_nombres = []
        for col in df.columns:
            for key in mapa:
                if key in str(col):
                    columnas_finales.append(col)
                    nuevos_nombres.append(mapa[key])
                    break
        
        df = df[columnas_finales]
        df.columns = nuevos_nombres
        
        df['Item'] = df['Item'].ffill()
        
        for idx, row in df.iterrows():
            total = row['Total']
            
            if pd.notna(total) and (pd.isna(row['Precio Unit.']) or row['Precio Unit.'] == '-'):
                
                if pd.notna(row['Cantidad']) and row['Cantidad'] != '-':
                    try:
                        cantidad = float(row['Cantidad'])
                        if cantidad > 0:
                            df.at[idx, 'Precio Unit.'] = total / cantidad
                    except:
                        pass
                else:
                    df.at[idx, 'Precio Unit.'] = total
        
        for idx, row in df.iterrows():
            total = row['Total']
            precio = row['Precio Unit.']
            
            if pd.notna(total) and pd.notna(precio) and precio != 0:
                if pd.isna(row['Cantidad']) or row['Cantidad'] == '-':
                    try:
                        df.at[idx, 'Cantidad'] = total / precio
                    except:
                        pass
        
        for idx, row in df.iterrows():
            if pd.notna(row['Cantidad']):
                try:
                    cantidad = float(row['Cantidad'])
                    if cantidad.is_integer():
                        df.at[idx, 'Cantidad'] = int(cantidad)
                except:
                    pass
        
        df = df.dropna(subset=['Total'])
        palabras_excluir = ['TOTAL 1 X', 'ADVANCE PAYMENT', 'BALANCE NEED TO PAY', 'TERM OF PAYMENT','CONSOLIDATE COST', 'OCEAN FREIGHT']  
        mask = ~df['Item'].astype(str).str.contains('|'.join(palabras_excluir), case=False, na=False)
        df = df[mask]
        
        print(f"\n {len(df)} ítems finales:\n")
        for i, (_, row) in enumerate(df.iterrows(), 1):
            print("="*60)
            print(f"FILA DETECTADA #{i}")
            print("="*60)
            
            for col in df.columns:
                valor = row[col]
                
                if col == 'Item':
                    item_str = str(valor) if pd.notna(valor) else "SIN ITEM"
                    print(f"{col.ljust(15)} : {item_str}")
                
                elif col in ['Precio Unit.', 'Total'] and pd.notna(valor):
                    print(f"{col.ljust(15)} : $ {float(valor):,.2f}")
                
                elif col == 'Cantidad' and pd.notna(valor):
                    try:
                        if float(valor).is_integer():
                            print(f"{col.ljust(15)} : {int(float(valor))}")
                        else:
                            print(f"{col.ljust(15)} : {float(valor):.2f}")
                    except:
                        print(f"{col.ljust(15)} : {valor}")
                
                elif col == 'Descripción':
                    desc = '-' if pd.isna(valor) else str(valor).replace('\n', ' // ')
                    print(f"{col.ljust(15)} : {desc}")
                
                else:
                    print(f"{col.ljust(15)} : {valor if pd.notna(valor) else '-'}")
            print()

    except Exception as e:
        print(f"Error: {e}")

leer_excel_dinamico('HBO 5887-7 PROFORMA INVOICE-2.xlsx')