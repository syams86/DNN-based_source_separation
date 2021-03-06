import torch
import torch.nn as nn
import torch.nn.functional as F
        
class GLU(nn.Module):
    """
    Gated Linear Units
    """
    def __init__(self, in_channels, out_channels):
        super().__init__()
        
        if out_channels is None:
            out_channels = in_channels
            
        self.in_channels, self.out_channels = in_channels, out_channels

        self.map = nn.Linear(in_channels, out_channels)
        self.map_gate = nn.Linear(in_channels, out_channels)
        
    def forward(self, input):
        """
        Args:
            input (batch_size, in_channels, *)
        Returns:
            output (batch_size, out_channels, *)
        """
        dim = input.dim()
        axis = tuple(range(dim))
        permutation = axis[0:1] + axis[:0:-1]
        
        input = input.permute(*permutation)
        x = self.map(input)
        x_sigmoid = self.map_gate(input)
        output = x * torch.sigmoid(x_sigmoid)
        output = output.permute(*permutation)
        
        return output


class GLU1d(nn.Module):
    """
    Gated Linear Units
    """
    def __init__(self, in_channels, out_channels):
        super().__init__()
        
        if out_channels is None:
            out_channels = in_channels
            
        self.in_channels, self.out_channels = in_channels, out_channels

        self.map = nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=1)
        self.map_gate = nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=1)
        
    def forward(self, input):
        """
        Args:
            input (batch_size, in_channels, T)
        Returns:
            output (batch_size, out_channels, T)
        """
        x = self.map(input)
        x_sigmoid = self.map_gate(input)
        output = x * torch.sigmoid(x_sigmoid)
        output = output.permute(*permutation)
        
        return output

class GLU2d(nn.Module):
    """
    Gated Linear Units
    """
    def __init__(self, in_channels, out_channels):
        super().__init__()
        
        if out_channels is None:
            out_channels = in_channels
            
        self.in_channels, self.out_channels = in_channels, out_channels

        self.map = nn.Conv2d(in_channels, out_channels, kernel_size=(1,1), stride=(1,1))
        self.map_gate = nn.Conv2d(in_channels, out_channels, kernel_size=(1,1), stride=(1,1))
        
    def forward(self, input):
        """
        Args:
            input (batch_size, in_channels, H, W)
        Returns:
            output (batch_size, out_channels, H, W)
        """
        x = self.map(input)
        x_sigmoid = self.map_gate(input)
        output = x * torch.sigmoid(x_sigmoid)
        output = output.permute(*permutation)
        
        return output

if __name__ == '__main__':
    batch_size = 4
    in_channels, out_channels = 3, 16
    
    print("="*10, "Gated Linear Units (GLU)", "="*10)
    # 1-D
    print("-"*10, "GLU1d", "-"*10)
    T = 128
    
    input = torch.randint(0, 5, (batch_size, in_channels, T), dtype=torch.float)

    glu1d = GLU(in_channels, out_channels)
    print(glu1d)

    output = glu1d(input)
    print(input.size(), output.size())
    print()
    
    # 2-D
    print("-"*10, "GLU2d", "-"*10)
    H, W = 512, 256

    input = torch.randint(0, 5, (batch_size, in_channels, H, W), dtype=torch.float)

    glu2d = GLU(in_channels, out_channels)
    print(glu2d)

    output = glu2d(input)
    print(input.size(), output.size())
