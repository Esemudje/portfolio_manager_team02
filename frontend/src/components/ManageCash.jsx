import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';

const ManageCash = () => {

    const [cashBalance, setCashBalance] = useState(0); 
    const [depositAmount, setDepositAmount] = useState('');
    const [withdrawAmount, setWithdrawAmount] = useState('');

    useEffect(() => {
        const fetchBalance = async () => {
            const balance = await apiService.getBalance(); 
            setCashBalance(Number(balance.cash_balance));
        };
        fetchBalance();
    }, []);

    const handleDeposit = async (e) => {
        e.preventDefault();

        if (isNaN(depositAmount) || depositAmount <= 0) {
        alert('Please enter a valid deposit amount');
        return;
    }
        await apiService.depositCash(Number(depositAmount));
        console.log('Depositing:', depositAmount, Number(depositAmount));
        setDepositAmount('');
        // Refresh balance from backend
        const balance = await apiService.getBalance();
        setCashBalance(Number(balance.cash_balance));
    };

    const handleWithdrawal = async (e) => {
        e.preventDefault();
        if (Number(withdrawAmount) <= cashBalance || isNaN(withdrawAmount) || withdrawAmount < 0) {
            await apiService.withdrawCash(Number(withdrawAmount));
            setWithdrawAmount('');
            // Refresh balance from backend
            const balance = await apiService.getBalance();
            setCashBalance(balance.cash_balance);
        } else {
            alert('Insufficient funds for withdrawal');
        }
    };

    return (
        <div className="stat-card">
            <div className="stat-value">${cashBalance.toFixed(2)}</div>
            <div className="stat-label">Current Cash Balance</div>
            <br />
        <form onSubmit={handleDeposit} style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px' }}>
                How much would you like to deposit?
                <input
                    type="number"
                    value={depositAmount}
                    onChange={(e) => {
                        console.log('Deposit input changed to:', e.target.value)
                        setDepositAmount(e.target.value)}}
                    min="0"
                    step="0.01"
                    required
                    style={{ marginLeft: '8px' }}
                />
            </label>
            <button
                className="btn btn-primary"
                type="submit"
                style={{ marginTop: '8px' }}
            >
                Deposit cash
            </button>
        </form>
        <br />
        <form onSubmit={handleWithdrawal} style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px' }}>
                How much would you like to withdraw?
                <input
                    type="number"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    min="0"
                    step="0.01"
                    required
                    style={{ marginLeft: '8px' }}
                />
            </label>
            <button
                className="btn btn-primary"
                type="submit"
                style={{ marginTop: '8px' }}
            >
                Withdraw cash
            </button>
    </form>
        </div>
    );
};

export default ManageCash;