using Microsoft.Extensions.Logging;

namespace Tests.Samples.CSharp;

/// <summary>
/// A compliant service demonstrating dependency injection and primary constructors.
/// </summary>
public class CompliantService(ILogger<CompliantService> logger, IUnitOfWorkFactory unitOfWorkFactory)
{
    private readonly ILogger<CompliantService> _logger = logger;
    private readonly IUnitOfWorkFactory _unitOfWorkFactory = unitOfWorkFactory;

    public void ProcessData()
    {
        using var uow = _unitOfWorkFactory.Create();
        _logger.LogInformation("Processing data within Unit of Work.");
        // Business logic...
    }
}

public interface IUnitOfWorkFactory
{
    IDisposable Create();
}
