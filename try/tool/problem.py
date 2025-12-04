# tool/problem.py

import pickle
import os
import pandas as pd
from langchain_core.tools import tool

DATA_DIR = "data"

@tool
def merge_pickles() -> str:
    """
    data 디렉토리에 있는 모든 pickle 파일(data1.pkl, data2.pkl, data3.pkl 등)을 
    하나의 DataFrame으로 병합합니다.
    
    Returns:
        str: 병합된 데이터의 행 수와 컬럼 정보를 포함한 요약 문자열
    """
    try:
        merged_data = []
        pickle_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.pkl')])
        
        if not pickle_files:
            return "data 디렉토리에 pickle 파일이 없습니다."
        
        for filename in pickle_files:
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                # DataFrame이면 그대로, 리스트면 DataFrame으로 변환
                if isinstance(data, pd.DataFrame):
                    merged_data.append(data)
                elif isinstance(data, list):
                    merged_data.append(pd.DataFrame(data))
                else:
                    merged_data.append(pd.DataFrame([data]))
        
        # 모든 데이터 병합
        merged_df = pd.concat(merged_data, ignore_index=True)
        
        # 전역 변수로 저장 (다음 tool에서 사용)
        global merged_dataframe
        merged_dataframe = merged_df
        
        return f"병합 완료: 총 {len(merged_df)}개의 리뷰, 컬럼: {list(merged_df.columns)}"
    
    except Exception as e:
        return f"병합 중 오류 발생: {str(e)}"

@tool
def filter_negative_reviews() -> str:
    """
    병합된 데이터에서 부정(Negative) 감정 리뷰만 필터링합니다.
    sentiment 컬럼이 'Negative'이거나 rating이 3 이하인 리뷰를 추출합니다.
    
    Returns:
        str: 필터링된 부정 리뷰의 개수와 기본 통계 정보
    """
    try:
        # 전역 변수에서 병합된 데이터 가져오기
        if 'merged_dataframe' not in globals():
            return "먼저 merge_pickles를 실행해주세요."
        
        df = merged_dataframe.copy()
        
        # 부정 감정 필터링 (sentiment 컬럼 또는 rating 컬럼 기준)
        if 'sentiment' in df.columns:
            negative_df = df[df['sentiment'].str.lower() == 'negative']
        elif 'rating' in df.columns:
            negative_df = df[df['rating'] <= 3]
        elif 'Sentiment' in df.columns:
            negative_df = df[df['Sentiment'].str.lower() == 'negative']
        else:
            return f"감정 정보를 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}"
        
        # 전역 변수로 저장 (분석에 사용)
        global negative_reviews_df
        negative_reviews_df = negative_df
        
        # 기본 통계
        result = f"부정 리뷰 필터링 완료: 총 {len(negative_df)}개\n"
        
        if 'age_group' in negative_df.columns:
            age_counts = negative_df['age_group'].value_counts()
            result += f"가장 많은 age_group: {age_counts.index[0]} ({age_counts.iloc[0]}개)\n"
        
        if 'product_category' in negative_df.columns:
            category_counts = negative_df['product_category'].value_counts()
            result += f"가장 많은 product_category: {category_counts.index[0]} ({category_counts.iloc[0]}개)\n"
        
        return result
    
    except Exception as e:
        return f"필터링 중 오류 발생: {str(e)}"