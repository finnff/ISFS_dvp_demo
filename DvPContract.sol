// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title DeliveryVersusPayment
 * @dev Atomic settlement contract for DvP transactions
 * Ensures both cash and securities transfer together or revert
 */
contract DeliveryVersusPayment {
    
    // Settlement event emitter
    event Settlement(
        address indexed trader,
        uint256 cashTokenId,
        uint256 securitiesTokenId,
        uint256 cashAmount,
        uint256 securitiesAmount,
        uint256 timestamp,
        uint256 gasUsed
    );
    
    // Track settlement count
    uint256 public settlementCount;
    
    // ERC20 interface for cash tokens
    interface IERC20 {
        function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
        function transfer(address recipient, uint256 amount) external returns (bool);
        function balanceOf(address account) external view returns (uint256);
        function approve(address spender, uint256 amount) external returns (bool);
    }
    
    /**
     * @dev Settle a trade atomically: transfer cash and securities together
     * @param trader The trader initiating the settlement
     * @param cashToken Cash/ERC20 token address
     * @param securitiesToken Securities/ERC20 token address
     * @param cashAmount Amount of cash to transfer
     * @param securitiesAmount Amount of securities to transfer
     * @param cashRecipient Address receiving cash (counterparty)
     * @param securitiesRecipient Address receiving securities (counterparty)
     */
    function settleTrade(
        address trader,
        address cashToken,
        address securitiesToken,
        uint256 cashAmount,
        uint256 securitiesAmount,
        address cashRecipient,
        address securitiesRecipient
    ) external returns (bool success) {
        uint256 startTime = block.timestamp;
        uint256 gasBefore = gasleft();
        
        // Transfer cash from trader to recipient (requires prior approval)
        require(
            IERC20(cashToken).transferFrom(trader, cashRecipient, cashAmount),
            "Cash transfer failed"
        );
        
        // Transfer securities from trader to recipient (requires prior approval)
        require(
            IERC20(securitiesToken).transferFrom(trader, securitiesRecipient, securitiesAmount),
            "Securities transfer failed"
        );
        
        uint256 gasUsed = gasBefore - gasleft();
        uint256 settlementTime = block.timestamp - startTime;
        
        // Emit event for dashboard
        settlementCount++;
        emit Settlement(
            trader,
            uint256(uint160(cashToken)),
            uint256(uint160(securitiesToken)),
            cashAmount,
            securitiesAmount,
            block.timestamp,
            gasUsed
        );
        
        return true;
    }
    
    /**
     * @dev Helper to check token balance
     */
    function getBalance(address token, address account) external view returns (uint256) {
        return IERC20(token).balanceOf(account);
    }
}
