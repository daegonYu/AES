import torch, configargparse
from data import load_asap_data
from model_architechure_bert_multi_scale_multi_loss import DocumentBertScoringModel

import gc
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def _initialize_arguments(p: configargparse.ArgParser):
    p.add('--bert_model_path', help='bert_model_path')
    p.add('--efl_encode', action='store_true', help='is continue training')
    p.add('--r_dropout', help='r_dropout', type=float)
    p.add('--batch_size', help='batch_size', type=int)
    p.add('--bert_batch_size', help='bert_batch_size', type=int)
    p.add('--cuda', action='store_true', help='use gpu or not')
    p.add('--device')
    p.add('--model_directory', help='model_directory')
    p.add('--test_file', help='test data file')
    p.add('--data_dir', help='data directory to store asap experiment data')
    p.add('--data_sample_rate', help='data_sample_rate', type=float)
    p.add('--prompt', help='prompt')
    p.add('--fold', help='fold')
    p.add('--chunk_sizes', help='chunk_sizes', type=str)
    p.add('--result_file', help='pred result file path', type=str)

    args = p.parse_args()
    args.test_file = "%s/p8_fold3_test.txt" % args.data_dir
    args.model_directory = "%s/%s_%s" % (args.model_directory, args.prompt, args.fold)
    args.bert_model_path = args.model_directory

    print('--------------------------------')
    print('GPU 사용 여부 : ', torch.cuda.is_available())
    if torch.cuda.is_available() and args.cuda:
        args.device = 'cuda'
    else:
        args.device = 'cpu'
    return args


if __name__ == "__main__":

    gc.collect()
    torch.cuda.empty_cache()
    # initialize arguments
    p = configargparse.ArgParser(default_config_files=["asap.ini"])
    args = _initialize_arguments(p)
    print(args)

    # load train data
    essay_points = pd.read_csv('./datatouch/korproject/kor_essayset2_point.csv',index_col=0)
    logical_points = essay_points.논리성.to_list()
    novelty_points = essay_points.참신성.to_list()
    persuasive_points = essay_points.설득력.to_list()
    reason_points = essay_points.풍부함.to_list()
    
    essays = pd.read_csv('./datatouch/korproject/kor_essayset2.csv', index_col=0)
    essays = essays.essay.to_list()
    
    tr_essay, test_essay, tr_logical_points, test_logical_points = train_test_split(essays, logical_points, test_size=0.2, random_state=321)
    tr_essay, test_essay, tr_novelty_points, test_novelty_points = train_test_split(essays, novelty_points, test_size=0.2, random_state=321)
    tr_essay, test_essay, tr_persuasive_points, test_persuasive_points = train_test_split(essays, persuasive_points, test_size=0.2, random_state=321)
    tr_essay, test_essay, tr_reason_points, test_reason_points = train_test_split(essays, reason_points, test_size=0.2, random_state=321)
    # tr_essay1 == tr_essay2 == tr_essay3 
    # test_essay1 == test_essay2 == test_essay3
    
    # 텍스트 데이터로 데이터 불러오기
    # if_sample=True
    # if if_sample:   # test data
    # train = load_asap_data('/home/daegon/Multi-Scale-BERT-AES/datatouch/prompt8_test.txt')
    # else:   # train data
    # train = load_asap_data('/home/daegon/Multi-Scale-BERT-AES/datatouch/prompt8_train.txt')

    # 텍스트 데이터 불러온 것 리스트에 추가
    # train_documents, train_labels = [], []        # 에세이별, 점수별
    # for _, text, label in train:
    #     train_documents.append(text)
    #     train_labels.append(label)
    
    # args에 저장된 test 경로에 해당하는 txt 파일 test set으로 불러오기
    # # load test data
    # # test = load_asap_data(args.test_file)
    # test = load_asap_data('/home/daegon/Multi-Scale-BERT-AES/datatouch/prompt8_test.txt')

    # 텍스트 데이터 불러온 것 리스트에 추가
    # test_documents, test_labels = [], []        # 에세이별, 점수별
    # for _, text, label in test:
    #     test_documents.append(text)
    #     test_labels.append(label)

    print("sample number:", len(essays))
    print("label number:", len(essay_points))

    # 기존 모델 불러오는 코드
    # model1 = DocumentBertScoringModel(args=args)
    # model2 = DocumentBertScoringModel(args=args)
    # model3 = DocumentBertScoringModel(args=args)
    
    
    # 모델 불러오기
    # load_model = True        
    
    # config = './models/chunk_model.bin1/config.json'    # config는 모두 같다.
    # 논리성 : 10 / 참신성 : 2 / 설득력 : 12
    
    # chunk_model_path =  './models/chunk_model.bin10'; word_doc_model_path = './models/word_doc_model.bin10' 
    # model1 = DocumentBertScoringModel(load_model=load_model,chunk_model_path=chunk_model_path,word_doc_model_path=word_doc_model_path,config=config,args=args)
    
    # chunk_model_path =  './models/chunk_model.bin2'; word_doc_model_path = './models/word_doc_model.bin2'
    # model2 = DocumentBertScoringModel(load_model=load_model,chunk_model_path=chunk_model_path,word_doc_model_path=word_doc_model_path,config=config,args=args)
    
    # chunk_model_path =  './models/chunk_model.bin12'; word_doc_model_path = './models/word_doc_model.bin12'
    # model3 = DocumentBertScoringModel(load_model=load_model,chunk_model_path=chunk_model_path,word_doc_model_path=word_doc_model_path,config=config,args=args)
    
    # 새로 학습 시키기
    model1 = DocumentBertScoringModel(load_model=False,args=args)
    model2 = DocumentBertScoringModel(load_model=False,args=args)
    model3 = DocumentBertScoringModel(load_model=False,args=args)
    # model4 = DocumentBertScoringModel(load_model=False,args=args)
    
    
    train_flag = True
    if train_flag:      # data는 튜플 형태, 길이: 2
        f = open('./loss_eval/eval.txt','a')
        f.write("\n\n--논리성--\n")
        f.close()
        data = (tr_essay, tr_logical_points)
        test = (test_essay, test_logical_points)
        model1.fit(data, test)
        print('-'*20)
        print('model1 finish')
        print('-'*20)
        
        f = open('./loss_eval/eval.txt','a')
        f.write("\n\n--참신성--\n")
        f.close()
        data = (tr_essay, tr_novelty_points)
        test = (test_essay, test_novelty_points)
        model2.fit(data, test)
        print('-'*20)
        print('model2 finish')
        print('-'*20)
        
        f = open('./loss_eval/eval.txt','a')
        f.write("\n\n--설득력--\n")
        f.close()
        data = (tr_essay, tr_persuasive_points)
        test = (test_essay, test_persuasive_points)    
        model3.fit(data, test)
        print('-'*20)
        print('model3 finish')
        print('-'*20)
        
        # f = open('./loss_eval/eval.txt','a')
        # f.write("\n\n--근거의 풍부함--\n")
        # f.close()
        # data = (tr_essay, tr_reason_points)
        # test = (test_essay, test_reason_points)
        # model4.fit(data, test)
        # print('-'*20)
        # print('model4 finish')
        # print('-'*20)
    
    # pearson, qwk 
    # model1.predict_for_regress((test_essay, test_logical_points))
    # model2.predict_for_regress((test_essay, test_novelty_points))
    # model3.predict_for_regress((test_essay, test_persuasive_points))
    # model4.predict_for_regress((test_essay, test_reason_points))

    # 예제넣고 결과 확인하기
    # input_sentence = [input()]      # list()와 []는 다르다.
    
    sentence = '전통은 지키고 악습은 끊어야 한다고 생각합니다.'
    input_sentence = [sentence,'']      # list()와 []는 다르다. // 이중 []로 batch 표현
    
    # 데이터 셋 넣고 표본 수집하기
    # hub_essays = pd.read_csv('./datatouch/korproject/AIHUB_대안제시_주장.csv', index_col=0)
    # sentences = hub_essays.essay_txt.to_list()
    
    logical_point_list = np.array([])
    novelty_point_list = np.array([])
    persuasive_point_list = np.array([])
    reason_point_list = np.array([])
    
    # for sentence in tr_essay:
    #     input_sentence =  [sentence,'']
        
    mode_ = 'logical'
    lp_ = model1.result_point(input_sentence =input_sentence ,mode_=mode_)  # 리턴 값은 float() 형, 범위 : 0~ 100
    logical_point_list = np.append(logical_point_list, lp_)
    
    mode_ = 'novelty'
    np_ = model2.result_point(input_sentence =input_sentence ,mode_=mode_)
    novelty_point_list = np.append(novelty_point_list, np_)
    
    mode_ = 'persuasive'
    pp_ = model3.result_point(input_sentence =input_sentence ,mode_=mode_)
    persuasive_point_list = np.append(persuasive_point_list, pp_)
    
    # mode_ = 'reason'
    # rp_ = model4.result_point(input_sentence =input_sentence ,mode_=mode_)
    # persuasive_point_list = np.append(reason_point_list, rp_)
    
    # np.save('./loss_eval/essay_point/logical',logical_point_list)
    # np.save('./loss_eval/essay_point/novelty',novelty_point_list)
    # np.save('./loss_eval/essay_point/persuasive',persuasive_point_list)
    # np.save('./loss_eval/essay_point/reason',reason_point_list)