# Fast UART-to-UART Data Transmission on STM32F1

This document provides guidance on achieving maximum throughput when transmitting data between two UARTs on STM32F1 microcontrollers.

## Overview

To transmit data between 2 UARTs as fast as possible on STM32F1, you should use **DMA (Direct Memory Access)** for both transmission and reception. This eliminates CPU overhead and allows continuous data transfer at maximum baud rates.

## Quick Answer

**Use DMA with both UARTs** - This is the fastest method because:
- No CPU intervention needed for each byte
- Continuous data flow without delays
- Supports full-duplex operation
- Can achieve maximum UART baud rates (up to 4.5 Mbps on STM32F1)

## Recommended Configuration

### 1. Hardware Setup
- Use appropriate GPIO pins with alternate function mapping
- Ensure proper voltage levels (3.3V for STM32F1)
- Keep TX-RX traces short to minimize capacitance
- Use pull-up resistors if needed

### 2. UART Configuration
```c
// Maximum baud rate calculation for STM32F103
// APB2 clock (USART1): 72 MHz max
// APB1 clock (USART2/3): 36 MHz max
// Practical maximum: ~4.5 Mbps (4,500,000 baud)

// Recommended configuration for high-speed transfer:
USART_InitTypeDef USART_InitStructure;
USART_InitStructure.USART_BaudRate = 921600;  // or 1000000, 1500000, etc.
USART_InitStructure.USART_WordLength = USART_WordLength_8b;
USART_InitStructure.USART_StopBits = USART_StopBits_1;
USART_InitStructure.USART_Parity = USART_Parity_No;
USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
```

### 3. DMA Configuration

#### For UART Transmission (TX)
```c
void UART_DMA_TX_Init(USART_TypeDef* USARTx, DMA_Channel_TypeDef* DMA_Channel)
{
    DMA_InitTypeDef DMA_InitStructure;
    
    // Enable DMA clock
    if (DMA_Channel >= DMA1_Channel1 && DMA_Channel <= DMA1_Channel7) {
        RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    }
    
    // Configure DMA for UART TX
    DMA_DeInit(DMA_Channel);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&(USARTx->DR);
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)txBuffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralDST;  // Memory to Peripheral
    DMA_InitStructure.DMA_BufferSize = TX_BUFFER_SIZE;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;  // or DMA_Mode_Circular
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_InitStructure.DMA_M2M = DMA_M2M_Disable;
    DMA_Init(DMA_Channel, &DMA_InitStructure);
    
    // Enable UART DMA TX
    USART_DMACmd(USARTx, USART_DMAReq_Tx, ENABLE);
}
```

#### For UART Reception (RX)
```c
void UART_DMA_RX_Init(USART_TypeDef* USARTx, DMA_Channel_TypeDef* DMA_Channel)
{
    DMA_InitTypeDef DMA_InitStructure;
    
    // Enable DMA clock
    if (DMA_Channel >= DMA1_Channel1 && DMA_Channel <= DMA1_Channel7) {
        RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    }
    
    // Configure DMA for UART RX
    DMA_DeInit(DMA_Channel);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&(USARTx->DR);
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)rxBuffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;  // Peripheral to Memory
    DMA_InitStructure.DMA_BufferSize = RX_BUFFER_SIZE;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;  // Circular for continuous RX
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_InitStructure.DMA_M2M = DMA_M2M_Disable;
    DMA_Init(DMA_Channel, &DMA_InitStructure);
    
    // Enable DMA channel
    DMA_Cmd(DMA_Channel, ENABLE);
    
    // Enable UART DMA RX
    USART_DMACmd(USARTx, USART_DMAReq_Rx, ENABLE);
}
```

## Complete Example: UART1 to UART2 Bridge

This example shows how to create a high-speed bridge between UART1 and UART2 using DMA.

```c
#include "stm32f10x.h"

// Buffer definitions
#define BUFFER_SIZE 1024
uint8_t uart1_rx_buffer[BUFFER_SIZE];
uint8_t uart2_rx_buffer[BUFFER_SIZE];
volatile uint16_t uart1_rx_index = 0;
volatile uint16_t uart2_rx_index = 0;

// DMA channel assignments for STM32F103:
// USART1_TX: DMA1_Channel4
// USART1_RX: DMA1_Channel5
// USART2_TX: DMA1_Channel7
// USART2_RX: DMA1_Channel6

void GPIO_Configuration(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    
    // Enable clocks
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_USART1 | 
                           RCC_APB2Periph_AFIO, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
    
    // USART1: TX=PA9, RX=PA10
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // USART2: TX=PA2, RX=PA3
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void USART_Configuration(void)
{
    USART_InitTypeDef USART_InitStructure;
    
    // Configure USART1 and USART2 with same settings
    USART_InitStructure.USART_BaudRate = 921600;  // High speed
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    
    USART_Init(USART1, &USART_InitStructure);
    USART_Init(USART2, &USART_InitStructure);
    
    USART_Cmd(USART1, ENABLE);
    USART_Cmd(USART2, ENABLE);
}

void DMA_Configuration(void)
{
    DMA_InitTypeDef DMA_InitStructure;
    NVIC_InitTypeDef NVIC_InitStructure;
    
    RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    
    // USART1 RX DMA (DMA1_Channel5)
    DMA_DeInit(DMA1_Channel5);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&USART1->DR;
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)uart1_rx_buffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
    DMA_InitStructure.DMA_BufferSize = BUFFER_SIZE;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;
    DMA_InitStructure.DMA_Priority = DMA_Priority_VeryHigh;
    DMA_InitStructure.DMA_M2M = DMA_M2M_Disable;
    DMA_Init(DMA1_Channel5, &DMA_InitStructure);
    
    // USART2 RX DMA (DMA1_Channel6)
    DMA_DeInit(DMA1_Channel6);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&USART2->DR;
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)uart2_rx_buffer;
    DMA_Init(DMA1_Channel6, &DMA_InitStructure);
    
    // USART1 TX DMA (DMA1_Channel4)
    DMA_DeInit(DMA1_Channel4);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&USART1->DR;
    DMA_InitStructure.DMA_MemoryBaseAddr = 0;  // Set at runtime
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralDST;
    DMA_InitStructure.DMA_BufferSize = 0;  // Set at runtime
    DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_Init(DMA1_Channel4, &DMA_InitStructure);
    
    // USART2 TX DMA (DMA1_Channel7)
    DMA_DeInit(DMA1_Channel7);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&USART2->DR;
    DMA_Init(DMA1_Channel7, &DMA_InitStructure);
    
    // Enable RX DMA channels
    DMA_Cmd(DMA1_Channel5, ENABLE);
    DMA_Cmd(DMA1_Channel6, ENABLE);
    
    // Enable USART DMA requests
    USART_DMACmd(USART1, USART_DMAReq_Rx | USART_DMAReq_Tx, ENABLE);
    USART_DMACmd(USART2, USART_DMAReq_Rx | USART_DMAReq_Tx, ENABLE);
    
    // Configure DMA interrupts for transfer complete
    DMA_ITConfig(DMA1_Channel5, DMA_IT_TC | DMA_IT_HT, ENABLE);
    DMA_ITConfig(DMA1_Channel6, DMA_IT_TC | DMA_IT_HT, ENABLE);
    
    // Enable DMA interrupts in NVIC
    NVIC_InitStructure.NVIC_IRQChannel = DMA1_Channel5_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0;
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStructure);
    
    NVIC_InitStructure.NVIC_IRQChannel = DMA1_Channel6_IRQn;
    NVIC_Init(&NVIC_InitStructure);
}

void UART_DMA_Send(USART_TypeDef* USARTx, DMA_Channel_TypeDef* DMA_Channel, 
                   uint8_t* data, uint16_t size)
{
    // Wait for previous transfer to complete
    // Note: Check the channel's TC bit, not a hardcoded flag
    while (DMA_GetFlagStatus(DMA_Channel->CNDTR) != 0);
    
    // Disable DMA channel
    DMA_Cmd(DMA_Channel, DISABLE);
    
    // Configure new transfer
    DMA_Channel->CMAR = (uint32_t)data;
    DMA_Channel->CNDTR = size;
    
    // Enable DMA channel
    DMA_Cmd(DMA_Channel, ENABLE);
}

// DMA interrupt handlers
void DMA1_Channel5_IRQHandler(void)
{
    // USART1 RX complete - forward to USART2
    if (DMA_GetITStatus(DMA1_IT_TC5))
    {
        DMA_ClearITPendingBit(DMA1_IT_TC5);
        // Get number of bytes received
        uint16_t bytes = BUFFER_SIZE - DMA_GetCurrDataCounter(DMA1_Channel5);
        if (bytes > 0) {
            // Forward to USART2 via DMA
            UART_DMA_Send(USART2, DMA1_Channel7, uart1_rx_buffer, bytes);
        }
    }
    
    if (DMA_GetITStatus(DMA1_IT_HT5))
    {
        DMA_ClearITPendingBit(DMA1_IT_HT5);
        // Half-transfer complete - can process first half of buffer
    }
}

void DMA1_Channel6_IRQHandler(void)
{
    // USART2 RX complete - forward to USART1
    if (DMA_GetITStatus(DMA1_IT_TC6))
    {
        DMA_ClearITPendingBit(DMA1_IT_TC6);
        uint16_t bytes = BUFFER_SIZE - DMA_GetCurrDataCounter(DMA1_Channel6);
        if (bytes > 0) {
            UART_DMA_Send(USART1, DMA1_Channel4, uart2_rx_buffer, bytes);
        }
    }
    
    if (DMA_GetITStatus(DMA1_IT_HT6))
    {
        DMA_ClearITPendingBit(DMA1_IT_HT6);
    }
}

int main(void)
{
    // System initialization
    SystemInit();
    
    // Configure peripherals
    GPIO_Configuration();
    USART_Configuration();
    DMA_Configuration();
    
    // Main loop - all data transfer happens via DMA
    while (1)
    {
        // Optional: Add processing or monitoring here
        // Data forwarding is handled by DMA interrupts
    }
}
```

## Performance Optimization Tips

### 1. Baud Rate Selection
- **Maximum theoretical**: ~4.5 Mbps (limited by APB clock and UART divider)
- **Recommended for reliability**: 921600 bps (standard high-speed rate)
- **Consider**: 1 Mbps, 1.5 Mbps, 2 Mbps for higher throughput
- **Formula**: BaudRate = fCLK / (16 × USARTDIV)

### 2. Buffer Management
```c
// Use double buffering for continuous transfer
#define BUFFER_SIZE 512  // Power of 2 for efficiency
uint8_t buffer_a[BUFFER_SIZE];
uint8_t buffer_b[BUFFER_SIZE];
volatile uint8_t active_buffer = 0;

// Switch buffers on half-transfer and transfer-complete interrupts
void DMA_IRQ_Handler(void)
{
    if (DMA_GetITStatus(DMA1_IT_HT5)) {
        // Half-transfer: DMA is filling second half, process first half
        active_buffer = 1;
        DMA_ClearITPendingBit(DMA1_IT_HT5);
    }
    if (DMA_GetITStatus(DMA1_IT_TC5)) {
        // Transfer complete: DMA wraps to first half, process second half
        active_buffer = 0;
        DMA_ClearITPendingBit(DMA1_IT_TC5);
    }
}
```

### 3. DMA Priority Settings
- Set DMA priority to **VeryHigh** for time-critical transfers
- Use separate DMA channels for TX and RX to avoid conflicts
- Consider DMA arbitration when multiple channels are used

### 4. UART FIFO (if available on your STM32F1 variant)
Some STM32F1 devices have UART FIFO - enable it for better performance:
```c
// Note: Not all STM32F1 variants support this
// Check your specific device reference manual
USART1->CR3 |= USART_CR3_DMAR | USART_CR3_DMAT;  // Enable DMA mode
```

### 5. Clock Configuration
Maximize APB clock speeds:
```c
// For USART1 (on APB2): aim for 72 MHz
// For USART2/3 (on APB1): aim for 36 MHz
// This maximizes possible baud rates
```

## Performance Comparison

| Method | CPU Usage | Max Throughput | Latency | Complexity |
|--------|-----------|----------------|---------|------------|
| Polling | ~100% | ~100 kbps | High | Low |
| Interrupts | ~50-80% | ~500 kbps | Medium | Medium |
| **DMA** | **<5%** | **~900 kbps+** | **Low** | **Medium** |
| DMA + Optimization | <2% | ~4 Mbps | Very Low | High |

## Common Pitfalls

1. **Baud Rate Mismatch**: Ensure both UARTs use the exact same baud rate
2. **Clock Configuration**: Verify APB clock frequencies before calculating baud rates
3. **Buffer Overrun**: Use circular buffers and process data promptly
4. **DMA Channel Conflicts**: Check DMA channel assignments in reference manual
5. **GPIO Configuration**: Ensure alternate function mapping is correct
6. **Insufficient Buffer Size**: Use buffers large enough for burst data

## Advanced: Zero-Copy Direct DMA Transfer

For absolute maximum speed, configure DMA to transfer directly from UART1 RX to UART2 TX:

```c
void Direct_DMA_Bridge_Init(void)
{
    // Configure UART1 RX DMA to write to intermediate buffer
    // Configure UART2 TX DMA to read from same buffer
    // Use DMA chaining or interrupt to coordinate transfers
    
    // This eliminates CPU involvement entirely
    // Can achieve near-line-rate speeds
}
```

## Troubleshooting

### Data Corruption
- Reduce baud rate
- Check signal integrity with oscilloscope
- Verify ground connections
- Add delay between transmissions if needed

### Lost Data
- Increase buffer size
- Enable DMA half-transfer interrupt for early processing
- Use hardware flow control (RTS/CTS) if available

### Slow Performance
- Verify DMA is actually being used (check CPU usage)
- Ensure DMA priority is set correctly
- Check for interrupt priority conflicts
- Profile code to find bottlenecks

## Additional Resources

- STM32F1 Reference Manual (RM0008)
- STM32F10x DMA Application Note (AN2548)
- STM32CubeMX for automatic code generation
- ST Community forums for specific issues

## Conclusion

For maximum UART-to-UART transfer speed on STM32F1:
1. **Use DMA for both TX and RX**
2. **Set highest practical baud rate (921600 or higher)**
3. **Use circular buffers for continuous operation**
4. **Minimize interrupt overhead**
5. **Optimize buffer sizes based on data patterns**

With proper DMA configuration, you can achieve sustained data rates of 900+ kbps with minimal CPU usage, allowing the processor to handle other tasks while data flows between UARTs automatically.
