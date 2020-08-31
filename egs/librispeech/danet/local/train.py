#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import torch
import torch.nn as nn

from utils.utils import set_seed
from dataset import SpectrogramTrainDataset, TrainDataLoader
from driver import Trainer
from models.danet import DANet
from criterion.distance import L2Loss
from criterion.pit import PIT2d

parser = argparse.ArgumentParser(description="Training of DANet (Deep Attractor Network)")

parser.add_argument('--wav_root', type=str, default=None, help='Path for dataset ROOT directory')
parser.add_argument('--train_json_path', type=str, default=None, help='Path for train.json')
parser.add_argument('--valid_json_path', type=str, default=None, help='Path for valid.json')
parser.add_argument('--sr', type=int, default=10, help='Sampling rate')
parser.add_argument('--window_fn', type=str, default='hamming', help='Window function')
# Model configuration
parser.add_argument('--fft_size', type=int, default=256, help='Window length')
parser.add_argument('--hop_size', type=int, default=None, help='Hop size')
parser.add_argument('--embed_dim', '-K', type=int, default=20, help='Embedding dimension')
parser.add_argument('--hidden_channels', '-H', type=int, default=600, help='hidden_channels')
parser.add_argument('--num_blocks', '-B', type=int, default=4, help='# LSTM layers')
parser.add_argument('--causal', type=int, default=0, help='Causality')
parser.add_argument('--mask_nonlinear', type=str, default='sigmoid', help='Non-linear function of mask estiamtion')
parser.add_argument('--n_sources', type=int, default=None, help='# speakers')
parser.add_argument('--criterion', type=str, default='l2loss', choices=['l2loss'], help='Criterion')
parser.add_argument('--optimizer', type=str, default='adam', choices=['sgd', 'adam'], help='Optimizer, [sgd, adam]')
parser.add_argument('--lr', type=float, default=0.001, help='Learning rate. Default: 0.001')
parser.add_argument('--weight_decay', type=float, default=0, help='Weight decay (L2 penalty). Default: 0')
parser.add_argument('--max_norm', type=float, default=None, help='Gradient clipping')
parser.add_argument('--batch_size', type=int, default=4, help='Batch size. Default: 128')
parser.add_argument('--epochs', type=int, default=5, help='Number of epochs')
parser.add_argument('--model_dir', type=str, default='./tmp/model', help='Model directory')
parser.add_argument('--loss_dir', type=str, default='./tmp/loss', help='Loss directory')
parser.add_argument('--sample_dir', type=str, default='./tmp/sample', help='Sample directory')
parser.add_argument('--continue_from', type=str, default=None, help='Resume training')
parser.add_argument('--use_cuda', type=int, default=1, help='0: Not use cuda, 1: Use cuda')
parser.add_argument('--overwrite', type=int, default=0, help='0: NOT overwrite, 1: FORCE overwrite')
parser.add_argument('--seed', type=int, default=42, help='Random seed')

def main(args):
    set_seed(args.seed)
    
    loader = {}
    
    train_dataset = SpectrogramTrainDataset(args.wav_root, args.train_json_path, fft_size=args.fft_size, hop_size=args.hop_size, window_fn=args.window_fn)
    valid_dataset = SpectrogramTrainDataset(args.wav_root, args.valid_json_path, fft_size=args.fft_size, hop_size=args.hop_size, window_fn=args.window_fn)
    print("Training dataset includes {} samples.".format(len(train_dataset)))
    print("Valid dataset includes {} samples.".format(len(valid_dataset)))
    
    loader['train'] = TrainDataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    loader['valid'] = TrainDataLoader(valid_dataset, batch_size=args.batch_size, shuffle=False)
    
    F_bin = args.fft_size//2 + 1
    model = DANet(F_bin, embed_dim=args.embed_dim, hidden_channels=args.hidden_channels, num_blocks=args.num_blocks, causal=args.causal, mask_nonlinear=args.mask_nonlinear, n_sources=args.n_sources)
    print(model)
    print("# Parameters: {}".format(model.num_parameters))
    
    if args.use_cuda:
        if torch.cuda.is_available():
            model.cuda()
            model = nn.DataParallel(model)
            print("Use CUDA")
        else:
            raise ValueError("Cannot use CUDA.")
    else:
        print("Does NOT use CUDA")
    
    # Optimizer
    if args.optimizer == 'sgd':
        optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)
    elif args.optimizer == 'adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    else:
        raise ValueError("Not support optimizer {}".format(args.optimizer))
        
    # Criterion
    if args.criterion == 'l2loss':
        criterion = L2Loss(reduction='mean')
    else:
        raise ValueError("Not support criterion {}".format(args.criterion))
    
    pit_criterion = PIT2d(criterion, n_sources=args.n_sources)
    
    trainer = Trainer(model, loader, pit_criterion, optimizer, args)
    trainer.run()

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    main(args)
