using Microsoft.Extensions.Logging;

namespace Tests.Samples.CSharp;

/// <summary>
/// A compliant service demonstrating dependency injection and primary constructors.
/// </summary>
/// <param name="logger">The logger instance for this service.</param>
/// <param name="unitOfWorkFactory">The factory to create Unit of Work instances.</param>
public class CompliantService(ILogger<CompliantService> logger, IUnitOfWorkFactory unitOfWorkFactory)
{
    private readonly ILogger<CompliantService> _logger = logger;
    private readonly IUnitOfWorkFactory _unitOfWorkFactory = unitOfWorkFactory;

    /// <summary>
    /// Processes data within a safe Unit of Work scope.
    /// </summary>
    public void ProcessData()
    {
        using var uow = _unitOfWorkFactory.Create();
        _logger.LogInformation("Processing data within Unit of Work.");
        // Business logic...
    }
}

/// <summary>
/// Factory interface for creating Unit of Work instances.
/// </summary>
public interface IUnitOfWorkFactory
{
    /// <summary>
    /// Creates a new Unit of Work instance.
    /// </summary>
    /// <returns>A disposable Unit of Work.</returns>
    IDisposable Create();
}
